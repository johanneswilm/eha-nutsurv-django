#!/usr/bin/env python

import csv
import json

states = set()

with open('2015_06_29_NNHS_2015_Selected EA_Final.xlsx - EA_2015.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    next(reader)
    for row in reader:
        state = row[0]
        if not state:
            continue
        states.add(state.upper())
    print json.dumps(list(states), indent=2, separators=(',', ': '))
