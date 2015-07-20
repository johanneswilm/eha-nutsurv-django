import csv
import json

with open('2015_06_29_NNHS_2015_Selected EA_Final.xlsx - EA_2015.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    clusterfile = {}
    for row in reader:
        clusterfile[row[5]] = {
            "cluster_name": row[4],
            "second_admin_level_name": row[2],
            "first_admin_level_name": row[0],
        }

    print json.dumps(clusterfile, indent=2, separators=(',', ': '))
