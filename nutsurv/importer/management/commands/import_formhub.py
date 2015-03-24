
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from dashboard.models import HouseholdSurveyJSON, Alert

from ...models import FakeTeams, update_mapping_documents_from_new_survey, reset_data

import csv
import re
import logging
from datetime import datetime

from pprint import pprint

SPLIT_SEGMENT_RE = re.compile("([^\[]*)(?:\[(\d+)\])?")

def find_household_members(data):
    members = []
    if 'consent' in data and 'hh_roster' in data['consent']:
        for fh_member in data['consent']['hh_roster']:
            member = {
                "firstName": fh_member['listing']['name'],
                "age": fh_member['listing']['age_years'],
            }
            if fh_member['listing']['sex'] == 1:
                member["gender"] = "M"
            else:
                member["gender"] = "F"

            members.append(member)

    return members

def parse_flat_formhub_csv(rawdata):
    parsed = {}
    for k, v in rawdata.items():
        path = k.split('/')

        put_here = parsed

        for segment_no, segment in enumerate(path):

            segment_name, in_array_pos = SPLIT_SEGMENT_RE.match(segment).groups()

            if in_array_pos != None:
                in_array_pos = int(in_array_pos)

            if not segment_name in put_here:
                if in_array_pos != None:
                    put_here[segment_name] = []
                else:
                    put_here[segment_name] = {}

            previous_put_here = put_here
            put_here = put_here[segment_name]

            if in_array_pos != None:
                while len(put_here) < in_array_pos:
                    put_here.append({})
                put_here = put_here[in_array_pos-1]

            if segment_no+1 == len(path):
                try:
                    v = float(v)
                    if v % 1 == 0.0:
                        v = int(v)
                except:
                    pass

                previous_put_here[segment_name] = v

    return parsed

class Command(BaseCommand):
    args = '<filename ...>'
    help = 'Imports the csv file'

    def handle(self, filename, **options):

        reset_data()

        last_10_seconds = None
        imported_last_10_seconds = 0

        with open(filename) as csvfile:

            headers = None

            for row_no, row in enumerate(csv.reader(csvfile, delimiter=',')):

                if not headers:
                    # first row is the headers
                    headers = row
                    continue

                rawdata = dict( ((k, v) for k, v in zip(headers, row) if v != 'n/a'))

                parsed = parse_flat_formhub_csv(rawdata)

                members = find_household_members(parsed)

                try:
                    household_survey, created = HouseholdSurveyJSON.objects.get_or_create(
                        uuid=parsed['_uuid'],
                        json={
                            "uuid": parsed['_uuid'],
                            "syncDate": parsed['_submission_time'] + ".000Z",
                            "startTime": parsed['starttime'],
                            "created": parsed['_submission_time']  + ".000Z",
                            "modified": parsed['_submission_time'],
                            "householdID": parsed['hh_number'],
                            "cluster": parsed['cluster'],
                            "endTime": parsed['endtime'],
                            "location": [
                                parsed['_gps_latitude'],
                                parsed['_gps_longitude']
                            ],
                            "members": members,
                            "team": FakeTeams.objects.get_or_create(team_id = \
                                parsed['team_num'])[0].json,
                            "_id": parsed['_uuid'],
                            "tools":{},
                            "history":[]
                        }
                    )
                except IntegrityError as e:
                    created = False
                except KeyError as e:
                    print e
                if created:
                    update_mapping_documents_from_new_survey(household_survey.json)
                    Alert.run_alert_checks_on_document(household_survey)

                if datetime.now().second/10 != last_10_seconds:
                    print "\n\n===> imported {} records in the last 10 seconds, that is {} records/s\n\n".format(imported_last_10_seconds, imported_last_10_seconds/10.0)
                    last_10_seconds = datetime.now().second/10
                    imported_last_10_seconds = 0
                else:
                    imported_last_10_seconds += 1

                print '[{}]'.format(datetime.now()), row_no, 'created' if created else 'exists', parsed['_uuid']

