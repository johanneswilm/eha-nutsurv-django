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

    models.reset_data()

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
    formhub_survey.save()
    formhub_survey.convert_to_household_survey()
    formhub_survey.save()

    if created:
        status = 201
    return JsonResponse(
        response,
        status=status
    )
