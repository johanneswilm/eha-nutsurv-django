
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from dashboard.models import HouseholdSurveyJSON, Alert

from ...models import FakeTeams, update_mapping_documents_from_new_survey, reset_data

from ... import anthrocomputation

import csv
import re
import logging
import math

from textwrap import dedent

from datetime import datetime

from pprint import pprint

SPLIT_SEGMENT_RE = re.compile("([^\[]*)(?:\[(\d+)\])?")

def find_household_members(data):

    if not 'consent' in data:
        return []

    members = []

    for fh_member in data['consent'].get('hh_roster', []):
        member = {
            "firstName": fh_member['listing']['name'],
            "age": fh_member['listing']['age_years'],
        }
        if fh_member['listing']['sex'] == 1:
            member["gender"] = "M"
        else:
            member["gender"] = "F"

        members.append(member)

    for fh_woman in data['consent'].get('note_7', []):

        if not 'womanname1' in fh_woman:
            logging.warning('Unnamed woman found, unable to find details..')
            continue

        name = fh_woman["womanname1"]
        member = next((item for item in members if item["firstName"] == name), None)

        if not member:
            logging.warning('Did not find woman named "%s" in this.', name)
            continue

        member["surveyType"] = "women"
        member["survey"] = {}

        if 'wom_muac' in fh_woman:
            member["survey"]["muac"] = fh_woman["wom_muac"]

    for fh_child in data['consent'].get('child', []):

        if not 'child_name' in fh_child:
            logging.warning('Unnamed child found, unable to find details..')
            continue

        name = fh_child["child_name"]

        member = next((item for item in members if item["firstName"] == name), None)

        if not member:
            logging.warning('Did not find details about child named "%s" in this.', name)
            continue

        if 'child_60' not in fh_child:
            logging.warning('No details available on child named "%s".', name)
            continue

        child_details = fh_child['child_60']

        member["surveyType"] = "child"

        if fh_child['date_known'] is 0:
            fh_child['age_months'] = None

        survey = {
            'muac': child_details.get('muac'),
            'height': child_details.get('height', None),
            'weight': child_details.get('weight', None),
            'ageInMonth': fh_child['age_months'],
            'edema': 'N' if child_details.get('edema', 0) == 0 else 'Y',
            'zscores': {},
        }

        zscores = anthrocomputation.keys_who_to_unicef(anthrocomputation.getAnthroResult(
            ageInDays=(fh_child['age_months'] or 0) * anthrocomputation.DAYSINMONTH,
            sex=member["gender"],
            weight=survey["weight"],
            height=survey["height"],
            isRecumbent=child_details.get('measure', None) == 2,
            hasOedema=survey["edema"] is 'Y',
            hc=None,
            muac=survey["muac"],
            tsf=None,
            ssf=None,
        ))

        for zscore_name in ('HAZ', 'WAZ', 'WHZ',):
            survey["zscores"][zscore_name] = zscores[zscore_name]

        member["survey"] = survey

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


def get_rawdata(headers, row):
    return dict(((k, v) for k, v in zip(headers, row) if v != 'n/a'))

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

                rawdata = get_rawdata(headers, row)

                parsed = parse_flat_formhub_csv(rawdata)

                members = find_household_members(parsed)

                try:
                    household_survey = HouseholdSurveyJSON(
                        uuid=parsed['_uuid'],
                        json={
                            "uuid": parsed['_uuid'],
                            "syncDate": parsed['_submission_time'] + ".000Z",
                            "startTime": parsed['starttime'],
                            "endTime": parsed['endtime'],
                            "created": parsed['_submission_time']  + ".000Z",
                            "modified": parsed['_submission_time'],
                            "householdID": parsed['hh_number'],
                            "cluster": parsed['cluster'],
                            "cluster_name": parsed['cluster_name'],
                            "state": parsed['state'],
                            "lga": parsed['lga'],
                            "location": [
                                parsed['_gps_latitude'],
                                parsed['_gps_longitude']
                            ],
                            "members": members,
                            "team_num": parsed['team_num'],
                            "team": FakeTeams.objects.get_or_create(
                                team_id=parsed['team_num']
                            )[0].json,
                            "_id": parsed['_uuid'],
                            "tools":{},
                            "history":[]
                        }
                    )
                    household_survey.save()
                except KeyError as e:
                    logging.error('%r', parsed)
                    logging.exception(e)


                update_mapping_documents_from_new_survey(household_survey.json)
                Alert.run_alert_checks_on_document(household_survey)

                if datetime.now().second/10 != last_10_seconds:
                    print dedent("""

                    ===> imported {} records in the last 10 seconds, that is {} records/s

                    """).format(imported_last_10_seconds, imported_last_10_seconds/10.0)

                    last_10_seconds = datetime.now().second/10
                    imported_last_10_seconds = 0
                else:
                    imported_last_10_seconds += 1

                print '[{}]'.format(datetime.now()), row_no, 'created' , parsed['_uuid'], len(members), 'household members'

