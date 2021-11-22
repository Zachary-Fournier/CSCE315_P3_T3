from django.shortcuts import render
from django.http import HttpResponse
from allauth.socialaccount.models import SocialToken

print("Printing social token...")
print(SocialToken)

# Create your views here.
def test(response, nm):
    return render(response, "main/testDynamic.html", {"num":nm})

def home(response):
    return render(response, "main/home.html", {"name":"Baszl"})
