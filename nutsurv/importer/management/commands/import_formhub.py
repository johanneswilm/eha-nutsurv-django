from django.core.management.base import BaseCommand, CommandError
from importer.models import FormhubSurvey

import csv
import re

from pprint import pprint

SPLIT_SEGMENT_RE = re.compile("([^\[]*)(?:\[(\d+)\])?")

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

        with open(filename) as csvfile:

            headers = None

            for row_no, row in enumerate(csv.reader(csvfile, delimiter=',')):

                if not headers:
                    headers = row
                    continue

                rawdata = dict( ((k, v) for k, v in zip(headers, row) if v != 'n/a'))

                parsed = parse_flat_formhub_csv(rawdata)

                formhub_survey, created = FormhubSurvey.objects.get_or_create(uuid=parsed['_uuid'])
                formhub_survey.json = parsed
                formhub_survey.save()
                formhub_survey.convert_to_household_survey()
                formhub_survey.save()
