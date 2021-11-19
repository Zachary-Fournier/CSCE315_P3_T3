from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def test(response, nm):
    return render(response, "main/testDynamic.html", {"num":nm})

def home(response):
    return render(response, "main/home.html", {"name":"Baszl"})