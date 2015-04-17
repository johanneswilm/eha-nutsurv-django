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
            [{'age': 30, 'first_name': 'Ismail', 'gender': 'M'},
             {'age': 22,
              'first_name': 'Lubabatu',
              'gender': 'F',
              'survey': {'muac': 276},
              'surveyType': 'women'}]
        )

    def test_smoke_find_household_members_zscores(self):
        rawdata = get_rawdata(self.headers, self.data[2])
        parsed = parse_flat_formhub_csv(rawdata)
        members = find_household_members(parsed)

        self.assertEqual(
            members[6],
            {'age': 1,
             'first_name': 'Umaru',
             'gender': 'M',
             'survey': {'ageInMonth': 12,
                        'edema': 'N',
                        'height': 71.8,
                        'muac': 158,
                        'weight': 9.4,
                        'zscores': {u'HAZ': -1.6579153301592868,
                                    u'WAZ': -0.23626655767549753,
                                    u'WHZ': 0.85}},
             'surveyType': 'child'}
        )
