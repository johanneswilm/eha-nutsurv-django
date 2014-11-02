from django.shortcuts import render

def dashboard(request):
    response = {}
    return render(request,'dashboard/index.html',response)

def home(request):
    response = {}
    return render(request,'dashboard/home.html',response)
