#!/usr/bin/env python

#    x    COLUMN NAMES

#    0    State_Name
#    1    State_code
#    2    Lga_name
#    3    Lga_code
#    4    EA_NAME
#    5    EA_code
#    6    EAsize
#    7    Unique ID
#    8    Reserve Cluster (RC)
#    9    PRIMARY
#   10    LOCALITY NAME

import csv
import json
import fileinput

reader = csv.reader(fileinput.input(), delimiter=',')
clusterfile = {}
for row in reader:
    if not any(row):
        continue
    clusterfile[row[7]] = {
      "cluster_name": row[4],
      "second_admin_level_name": row[2],
      "first_admin_level_name": row[0],
    }

print json.dumps(clusterfile, indent=2, separators=(',', ': '))
