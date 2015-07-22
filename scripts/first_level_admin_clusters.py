import csv
import json

with open('2015_06_29_NNHS_2015_Selected EA_Final.xlsx - EA_2015.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    clusterfile = {}
    next(reader)
    for row in reader:
        clusterfile[row[0].upper()] = {
            # FIXME this should be a real count of enumeration areas
            # (EA/EA_NAME) per state (see #592) e.g.:
            # { ABIA: { standard: 32, reserve: 4 } }
            "reserve": 5,
            "standard": 10
        }

    print json.dumps(clusterfile, indent=2, separators=(',', ': '))
