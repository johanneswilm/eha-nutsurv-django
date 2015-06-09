import uuid
import random
import logging

from datetime import datetime
from jsonfield import JSONField

from django.db import models

from dashboard import models as dashboard_models

from pytz import timezone
import dateutil.parser


def reset_data():
    FakeTeams.objects.all().delete()
    dashboard_models.HouseholdSurveyJSON.objects.all().delete()
    dashboard_models.Alert.objects.all().delete()

    dashboard_models.Clusters.objects.all().delete()
    cluster_data = dashboard_models.Clusters()
    cluster_data.json = {}
    cluster_data.name_or_id = 'default_clusters'
    cluster_data.active = True
    cluster_data.save()

    dashboard_models.FirstAdminLevelsReserveClusters.objects.all().delete()
    first_admin_level_reserve_data = dashboard_models.FirstAdminLevelsReserveClusters()
    first_admin_level_reserve_data.json = []
    first_admin_level_reserve_data.name_or_id = 'default_first_admin_level_reserve_data'
    first_admin_level_reserve_data.active = True
    first_admin_level_reserve_data.save()

    dashboard_models.ClustersPerFirstAdminLevel.objects.all().delete()
    cluster_first_admin_level_data = dashboard_models.ClustersPerFirstAdminLevel()
    cluster_first_admin_level_data.json = {}
    cluster_first_admin_level_data.name_or_id = 'default_clusters_per_first_admin_level'
    cluster_first_admin_level_data.active = True
    cluster_first_admin_level_data.save()

    dashboard_models.FirstAdminLevels.objects.all().delete()
    first_admin_level_data = dashboard_models.FirstAdminLevels()
    first_admin_level_data.json = []
    first_admin_level_data.name_or_id = 'default_first_admin_levels'
    first_admin_level_data.active = True

    first_admin_level_data.save()


def convert_to_utc_js_datestring(date_string):
    """Turn '2014-05-05T17:26:37.401+01' into '2014-05-05T16:26:37.401Z'"""
    parsed_date = dateutil.parser.parse(date_string)
    return parsed_date.astimezone(timezone('UTC')).isoformat()[:-6] + 'Z'


def update_mapping_documents_from_new_survey(json):
    # Check whether other pieces of info are there as they should be.

    for key in ('state', 'cluster', 'cluster_name', 'lga',):
        if key not in json:
            logging.warning('{!r} not in {!r}'.format(key, json))  # just to make sure it's there
            return

    cluster_data = dashboard_models.Clusters.get_active()
    if cluster_data is None:
        return

    cluster_number = str(json['cluster'])
    # We make everything depend on the existence of the cluster number in the cluster db.
    if cluster_number in cluster_data.json:
        return

    cluster_data.json[cluster_number] = {
        "cluster_name": json['cluster_name'],
        # These are numbers we turn into strings. We don't have names. Better than nothing.
        "second_admin_level_name": str(json['lga']),
        # These are numbers we turn into strings. We don't have names. Better than nothing.
        "first_admin_level_name": str(json['state'])
    }
    cluster_data.save()

    first_admin_level_number = str(json['state'])
    cluster_first_admin_level_data = dashboard_models.ClustersPerFirstAdminLevel.get_active()
    if first_admin_level_number not in cluster_first_admin_level_data.json:
        cluster_first_admin_level_data.json[first_admin_level_number] = {
            "standard": 10,
            "reserve": 5
        }
        cluster_first_admin_level_data.save()

    first_admin_level_data = dashboard_models.FirstAdminLevels.get_active()
    if first_admin_level_number not in first_admin_level_data.json:
        first_admin_level_data.json.append(first_admin_level_number)
        first_admin_level_data.save()


FIRST_NAMES = [
    ['Abubakar', 'M'],
    ['Omoshola', 'M'],
    ['Eterigho', 'M'],
    ['Anayuchukwu', 'M'],
    ['Polonololgombi', 'M'],
    ['Tolulope', 'M'],
    ['Adenuga', 'M'],
    ['Segbuyota', 'M'],
    ['Toheeb', 'M'],
    ['Omotoyosi', 'M'],
    ['Oludare', 'M'],
    ['Ikor', 'M'],
    ['Oritsefemi', 'M'],
    ['Gana', 'M'],
    ['Umo', 'F'],
    ['Faderera', 'F'],
    ['Doris', 'F'],
    ['Chika', 'F'],
    ['Safiya', 'F'],
    ['Olapeju', 'F'],
    ['Ihuoma', 'F'],
    ['Chidera', 'F'],
    ['Rofiat', 'F'],
    ['Adeola', 'F'],
    ['Osifo', 'F'],
    ['Iquo', 'F'],
    ['Doyinsola', 'F'],
    ['Agbonrein', 'F'],
    ['Oselumen', 'F'],
    ['Adenze', 'F'],
    ['Idubu', 'F'],
    ['Ashabi', 'F'],
]

LAST_NAMES = [
    'Azikiwe',
    'Chahine',
    'Bello',
    'Cisse',
    'Akintola',
    'Okotie',
    'Nzeogwu',
    'Onwuatuegwu',
    'Okafor',
    'Contee',
    'Okeke',
    'Conteh',
    'Okoye',
    'Diallo',
    'Obansanjo',
]

EMAIL_PROVIDERS = [
    'gmail.com',
    'hotmail.com',
    'oni.com',
    'yahoo.com',
]


class FakeTeams(models.Model):

    """The data from Formhub comes without team member data. For the test
    import through CSV we therefore create fake teams with random team members.
    This should likely be removed before import data from formhub for realworld
    usage.
    """

    json = JSONField(null=True, blank=True, help_text=' ')
    team_id = models.IntegerField(unique=True)

    def __unicode__(self):
        return str(self.team_id)

    def save(self, *args, **kwargs):
        if not self.json:
            # If the team does not yet exist, create random team data.
            team_leader = [random.choice(FIRST_NAMES),
                           random.choice(LAST_NAMES)]
            anthropometrist = [random.choice(FIRST_NAMES),
                               random.choice(LAST_NAMES)]
            assistant = [random.choice(FIRST_NAMES),
                         random.choice(LAST_NAMES)]
            self.json = {
                "uuid": str(uuid.uuid4()),
                # Trying to get a date/time stamp as JS outputs it.
                "created": datetime.utcnow().isoformat()[:-3] + 'Z',
                # TODO: Using a UUID here for now. not sure this is OK.
                "_rev": str(uuid.uuid4()),
                # Trying to get a date/time stamp as JS outputs it.
                "modified": datetime.utcnow().isoformat()[:-3] + 'Z',
                "teamID": self.team_id,
                "members": [
                    {
                        "designation": "Team Leader",
                        "firstName": team_leader[0][0],
                        "mobile": "0" +
                        str(random.randint(10000000000, 99999999999)),
                        "lastName": team_leader[1],
                        "birthYear": random.randint(1900, 2015),
                        "memberID": self.team_id * 3,
                        "gender": team_leader[0][1],
                        "email": team_leader[0][0] + '.' + team_leader[1] + '@' + random.choice(EMAIL_PROVIDERS)
                    },
                    {
                        "designation": "Anthropometrist",
                        "firstName": anthropometrist[0][0],
                        "mobile":"0" +
                        str(random.randint(10000000000, 99999999999)),
                        "lastName": anthropometrist[1],
                        "birthYear": random.randint(1900, 2015),
                        "memberID": self.team_id * 3 + 1,
                        "gender": anthropometrist[0][1],
                        "email": anthropometrist[0][0] + '.' + anthropometrist[1] + '@' + random.choice(EMAIL_PROVIDERS)
                    },
                    {
                        "designation": "Assistant",
                        "firstName": assistant[0][0],
                        "mobile":"0" +
                        str(random.randint(10000000000, 99999999999)),
                        "lastName": assistant[1],
                        "birthYear": random.randint(1900, 2015),
                        "memberID": self.team_id * 3 + 2,
                        "gender": assistant[0][1],
                        "email": assistant[0][0] + '.' + assistant[1] + '@' + random.choice(EMAIL_PROVIDERS)
                    }],
                "_id": str(uuid.uuid4())
            }
            super(FakeTeams, self).save(*args, **kwargs)
