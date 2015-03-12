import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse

from . import models

from dashboard import models as dashboard_models

@login_required
def importer(request):
    response = {}
    # If a post_key is specified in the settings we use
    # it as a "security" measure
    post_key = getattr(settings, "POST_KEY", None)
    if post_key:
        response['POST_KEY'] = post_key
    return render(request, 'importer/index.html', response)

@require_POST
def reset_data(request):
    response = {}
    models.FakeTeams.objects.all().delete()
    models.FormhubSurvey.objects.all().delete()
    dashboard_models.HouseholdSurveyJSON.objects.all().delete()
    dashboard_models.Alert.objects.all().delete()

    dashboard_models.ClustersJSON.objects.all().delete()
    cluster_data = dashboard_models.ClustersJSON()
    cluster_data.json = {
        "clusters": {}
    }
    cluster_data.save()

    dashboard_models.ClustersPerTeam.objects.all().delete()
    team_data = dashboard_models.ClustersPerTeam()
    team_data.json = {}
    team_data.name_or_id = 'default_clusters_per_team'
    team_data.active = True
    team_data.save()

    dashboard_models.ClustersPerState.objects.all().delete()
    cluster_state_data = dashboard_models.ClustersPerState()
    cluster_state_data.json = {}
    cluster_state_data.name_or_id = 'default_clusters_per_state'
    cluster_state_data.active = True
    cluster_state_data.save()

    dashboard_models.States.objects.all().delete()
    states_data = dashboard_models.States()
    states_data.json = []
    states_data.name_or_id = 'default_states'
    states_data.active = True
    states_data.save()

    status = 200
    return JsonResponse(
        response,
        status=status
    )


@csrf_exempt
@require_POST
def register_formhub_survey(request):

    # If a post_key is specified in the settings we use
    # it as a "security" measure
    post_key = getattr(settings, "POST_KEY", None)

    if post_key:
        if "key" in request.GET:
            if request.GET["key"] != post_key:
                #The request has a key but it doesn't match
                return HttpResponseForbidden()
        else:
            #The post key is specified in the settings but not in the URL
            return HttpResponseBadRequest()

    try:
        json_object = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest()

    response={}
    status = 200

    formhub_survey, created = models.FormhubSurvey.objects.get_or_create(uuid=json_object['_uuid'])
    formhub_survey.json = json_object
    print formhub_survey.uuid
    formhub_survey.save()
    formhub_survey.convert_to_household_survey()
    formhub_survey.save()

    if created:
        status = 201
    return JsonResponse(
        response,
        status=status
    )
