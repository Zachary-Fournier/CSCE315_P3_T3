from django.forms.fields import CharField
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import TextInput, PasswordInput
from main.models import BaszlAccount

# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                newUser = BaszlAccount(baszlUser=request.POST['username'])
                newUser.save()
                form.save()
                user = authenticate(request, username=request.POST['username'], password=request.POST['password1'])
                login(request, user)
                return redirect("/platformsLogin/")
                
            except Exception as e:
                return redirect("/login/1")
        else:
            return redirect("/login/2")
  
    return redirect("/login/")

def login_view(request, errCode=0):
    errorMsg = ""
    if request.method == "POST":
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            # Return an 'invalid login' error message.
            errorMsg = "Invalid login. Please enter correct username and password."
    else:
        if errCode == 1:
            # Couldn't register
            errorMsg = "Couldn't save new account."
        elif errCode == 2:
            # Invalid form
            errorMsg = "Invalid registration form."

    form = AuthenticationForm()
    rform = RegisterForm()
    
    return render(request, "login/login.html", {"form":form, "rform":rform, "errorMsg":errorMsg})

def logout_view(request):
    logout(request)
    return redirect("/")

def changePassword(response):
    return HttpResponse("Working on it")