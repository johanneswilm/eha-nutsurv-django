from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf

def user_login(request):
    response = {}
    response['state'] = ""
    username = password = ''
    response.update(csrf(request))
    if request.GET:
        response['next'] = request.GET.get('next')
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        response['next'] = request.POST.get('next')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if response['next']:
                    return HttpResponseRedirect(response['next'])
                response['state'] = "You're successfully logged in!"
            else:
                response['state'] = "Your account is not active, please contact the site admin."
        else:
            response['state'] = "Your username and/or password were incorrect."
    response['username'] = username
    return render_to_response('accounts/login.html',response)

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')
