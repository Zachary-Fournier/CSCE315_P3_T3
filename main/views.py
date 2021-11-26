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

    return render(request, "main/home.html", {"name":"Baszl"})
        

def dashboard(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/login/")

    return render(request, "main/dashboard.html")

def makePost(request):
    return HttpResponse("<h1>Howdy</h1>")