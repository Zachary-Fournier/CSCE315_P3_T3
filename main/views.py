from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from allauth.socialaccount.models import SocialToken
from django.contrib.auth.models import User

print("Printing social token...")
print(SocialToken)


# Create your views here.
def test(request, nm):
    return render(request, "main/testDynamic.html", {"num":nm})

def home(request):
    twtHandle=igHandle=fbHandle = "Not Connected"

    if not request.user.is_authenticated:
        return HttpResponseRedirect("/login/")

    return render(request, "main/dashboard.html", {"twtHandle":twtHandle, "igHandle":igHandle, "fbHandle":fbHandle})
        

def platformsLogin(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/login/")

    if request.method == "POST":
        # Use information, such as token
        x = 0
    else:
        #
        x = 1

    return render(request, "main/platformsLogin.html", {})

def makePost(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            message = request.POST.get("postText")
            if message:
                noPost = True
                # Something actually posted
                if request.POST.get("facebook"):
                    noPost *= False
                    print("Posting Facebook...")
                if request.POST.get("twitter"):
                    noPost *= False
                    print("Posting Twitter...")
                if request.POST.get("instagram"):
                    noPost *= False
                    print("Posting Instagram...")
                if noPost:
                    print("No post")
                else:
                    print(message)
                    # user.account.numPosts += 1
        return redirect("/")
    else:
        return HttpResponse("You are not authorized for this activity")