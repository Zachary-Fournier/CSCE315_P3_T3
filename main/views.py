from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from allauth.socialaccount.models import SocialToken
from django.contrib.auth.models import User

print("Printing social token...")
print(SocialToken)


# Create your views here.
def test(request, nm):
    return render(request, "main/testDynamic.html", {"num":nm})

def home(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/login/")

    return render(request, "main/dashboard.html", {})
        

def platformsLogin(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/login/")

    return render(request, "main/platformsLogin.html", {})

def makePost(request, message):
    if request.user.is_authenticated:
        # Do something
        return HttpResponse(str(message))
    else:
        return HttpResponse("You are not authorized for this activity")