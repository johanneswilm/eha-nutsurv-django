'''
Usage: `curl -u <username>:<password>  https://forms.eocng.org/<username>/forms/NNHS_2015/data.json | NUTSURV_DOMAIN='http://some_nutsurver:port' python ./formhub_importer.py `

This script takes all the json surveys from formhub to upload them to the nutsurv server of your choice.
'''

import requests
import json
from collections import defaultdict
from datetime import date, timedelta
import fileinput
import os
import dateutil.parser


lines = ''.join(l for l in fileinput.input())
raw_json = json.loads(lines)

NUTSURV_DOMAIN = os.getenv('NUTSURV_DOMAIN', 'http://nutsurv-dev.eocng.org')
TEAM_MEMBER_URL = NUTSURV_DOMAIN + '/dashboard/teammembers/%s/'


class Struct(defaultdict):
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __getattr__(self, name):
        return self.__dict__.get(name, None)


def simplify_keys(obj):
    '''
    Some keys are 'consent/note_begin_woman/wom_muac' and this keeps the 'wom_muac'
    '''
    if isinstance(obj, list):
        return [simplify_keys(v) for v in obj]
    elif isinstance(obj, dict):
        return dict((k.split('/')[-1], simplify_keys(v)) for k, v in obj.items())
    return obj

surveys = simplify_keys(raw_json)
null = None


def format(clusters):
    for formhub_survey in surveys:
        s = Struct(**formhub_survey)
        members = []
        women = dict((w['womanname1'], w) for w in s.note_begin_woman or [] if 'womanname1' in w)  # Look on my works and dispair.
        children = dict((c['child_name'], c) for c in (s.child or []) if 'child_name' in c)

        # print json.dumps(formhub_survey, sort_keys=True, indent=4)
        # print '=' * 10
        for i, m in enumerate(s.hh_roster or []):
            m = Struct(**m)
            w = Struct(**women.get(m.name, {}))
            c = Struct(**children.get(m.name, {}))

            starttime = dateutil.parser.parse(s.starttime)
            birthdate = m.age_years != '999' and (date.today() - timedelta(days=int(m.age_years or 0) * 356)).isoformat()

            members += [{
                        "index": i,
                        "firstName": m.name,
                        "birthdate": birthdate,
                        "gender": m.sex == '2' and 'F' or 'M',
                        "muac": int(c.muac or w.wom_muac or 0),
                        "weight": float(c.weight or 0),
                        "height": float(c.height or 0),
                        "heightType": c.measure == '2' and 'recumbent' or 'standing',
                        "extraQuestions": {
                            "age_months": int(c.age_months or 0)  # I'm so sorry.
                        },
                        "edema": int(c.edema or 0)
                        }]

        nutsurv_survey = {
            "uuid": s.instanceID.split(":")[1],
            "householdNumber": int(s.hh_number),
            "members": members,
            "teamLead": TEAM_MEMBER_URL % s.team_leader_num,
            "teamAssistant": TEAM_MEMBER_URL % s.team_leader_num,
            "teamAnthropometrist": TEAM_MEMBER_URL % s.team_leader_num,
            "startTime": s.starttime,
            "endTime": s.endtime,
            "location": {
                "type": "Point",
                "coordinates": [
                    float(s.gps.split()[0]),
                    float(s.gps.split()[1])
                ]
            }
        }

        cluster = {
            "firstAdminLevel": "",
            "secondAdminLevel": "",
            "cluster": int(s.cluster),
            "clusterName": s.cluster_name,
        }

        if s.cluster in clusters:
            c = clusters[s.cluster]
            cluster["firstAdminLevel"] = c["first_admin_level_name"]
            cluster["secondAdminLevel"] = c["second_admin_level_name"]

        nutsurv_survey.update(cluster)

        out = json.dumps(nutsurv_survey, sort_keys=True, indent=4)
        #print out
        url = NUTSURV_DOMAIN + "/dashboard/surveys/"
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=out, headers=headers)
        #print r.json()

dirname = os.path.dirname(os.path.realpath(__file__))
cluster_file = os.path.join(dirname, 'default_clusters.json')

with open(cluster_file) as raw_clusters:
    clusters = json.load(raw_clusters)
    format(clusters)
