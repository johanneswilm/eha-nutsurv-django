from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def importer(request):
    response = {}
    return render(request, 'importer/index.html', response)
