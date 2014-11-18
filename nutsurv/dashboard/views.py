from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    response = {}
    return render(request,'dashboard/index.html',response)

@login_required
def home(request):
    response = {}
    return render(request,'dashboard/home.html',response)

@login_required
def mapping_checks(request):
    response = {}
    return render(request,'dashboard/mapping_checks.html',response)

@login_required
def age_distribution(request):
    response = {}
    return render(request,'dashboard/age_distribution.html',response)


@login_required
def survey_completed(request):
    response = {}
    return render(request,'dashboard/survey_completed.html',response)

@login_required
def survey_completed_teams(request):
    response = {}
    return render(request,'dashboard/survey_completed_teams.html',response)

@login_required
def survey_completed_states(request):
    response = {}
    return render(request,'dashboard/survey_completed_states.html',response)
