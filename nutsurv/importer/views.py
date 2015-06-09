from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from . import models

from .management.commands.import_formhub import Command


@login_required
def import_csvfile(request):
    models.reset_data()

    message = None
    if request.method == 'POST' and 'csv_file' in request.FILES:
        Command().import_csvfile(request.FILES['csv_file'])
        message = "Import successful."

    return render(request, 'importer/import.html', dictionary={
        "message": message
    })


@require_POST
def reset_data(request):
    response = {}

    models.reset_data()

    status = 200
    return JsonResponse(
        response,
        status=status
    )
