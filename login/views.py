from django.forms.fields import CharField
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import TextInput, PasswordInput

# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(request, username=request.POST['username'], password=request.POST['password1'])
            login(request, user)
            return redirect("/platformsLogin/")
        else:
            form = RegisterForm()
    else:
        form = RegisterForm()
  
    return render(request, "login/login.html", {"rform":form})

def login_view(request):
    errorMsg = ""
    if request.method == "POST":
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            # Return an 'invalid login' error message.
            errorMsg = "Invalid login. Please enter correct username and password."
    form = AuthenticationForm()
    rform = RegisterForm()
    
    return render(request, "login/login.html", {"form":form, "rform":rform, "errorMsg":errorMsg})

def logout_view(request):
    logout(request)
    return redirect("/")

def changePassword(response):
    return HttpResponse("Working on it")