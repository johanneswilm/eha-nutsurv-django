from django.test import TestCase
from .management.commands.import_formhub import parse_flat_formhub_csv, find_household_members, get_rawdata

import csv
import os

filename = '{}/tests/5_records_of_NNHS_R1_2014 Final Data Qst_version_10Feb14_2014_07_28.csv'.format(
    os.path.dirname(__file__)
)

class ImporterTests(TestCase):

    def setUp(self):
        with open(filename) as csvfile:
            all_data = list(csv.reader(csvfile, delimiter=','))
            self.headers = all_data[0]
            self.data = all_data[1:]

    def test_smoke_parse_flat_formhub_csv(self):
        rawdata = get_rawdata(self.headers, self.data[1])
        parsed = parse_flat_formhub_csv(rawdata)
        self.assertEqual(
            parsed['consent']['hh_roster'][0]['listing']['age_years'],
            30
        )

    def test_smoke_find_household_members(self):
        rawdata = get_rawdata(self.headers, self.data[1])
        parsed = parse_flat_formhub_csv(rawdata)
        members = find_household_members(parsed)
        self.assertEqual(
            members,
            [{'age': 30, 'firstName': 'Ismail', 'gender': 'M'},
             {'age': 22,
              'firstName': 'Lubabatu',
              'gender': 'F',
              'survey': {'muac': 276},
              'surveyType': 'women'}]
        )
