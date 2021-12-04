from logging import error
import re
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect, response
from allauth.socialaccount.models import SocialToken
from django.contrib.auth.models import User
import tweepy
import facebook 
from instabot import Bot
from .models import *
import shutil
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def getKey(string):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt= b',\x1b%\xb2\xc8\xd1\xedBL\xf1\x1er8\xc1\xf6V',
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(string.encode()))

consumer_key = '1OT7fMp7nItZHuuXNwv0duBs2'
consumer_secret = 'zUAsq7LIlNPzxPOuIvWWQ9uqGoG1YUJ12uD7qzK5obWmebViVr'

AUTH = tweepy.OAuthHandler(consumer_key, consumer_secret, 'https://baszl.herokuapp.com/twitteraccess/')

# Create your views here.
def test(request, nm):
    return render(request, "main/testDynamic.html", {"num":nm})

def home(request):
    twtHandle=igHandle=fbHandle = "Not Connected"
    fbPosts=igPosts=twtPosts = 0

    if not request.user.is_authenticated:
        return HttpResponseRedirect("/login/")

    return render(request, "main/dashboard.html", {"twtHandle":twtHandle, "igHandle":igHandle, "fbHandle":fbHandle, "numFbPosts":fbPosts, "numIgPosts":igPosts, "numTwtPosts":twtPosts})
        

def platformsLogin(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/login/")
    #print(SocialToken.objects.get(account__user=request.user, account__provider='facebook'))

    if request.method == "POST":
        # Use information, such as token
        access_token = SocialToken.objects.get(account__user=request.user, account__provider='facebook') #get instead of filter (you need only one object)
        r = request.get('https://graph.facebook.com/me?access_token='+access_token.token+'&fields=id,name,email') #add access_token.token to your request
    else:
        pass

    return render(request, "main/platformsLogin.html", {})

def getFacebookToken(request, token):
    # Save to account
    user = BaszlAccount.objects.get(baszlUser=request.user.username)
    fernet = Fernet(getKey(request.user.username))
    user.facebookaccount_set.update_or_create(accessToken=fernet.encrypt(token))

    return redirect("/platformsLogin/")

def getTwitterToken(request):
    try:
        return redirect(AUTH.get_authorization_url())
    except Exception as e:
        return redirect("/platformsLogin/")

def getTwitterAccess(request):
    try:
        verifier = request.GET.get('oauth_verifier')
        key = request.GET.get('oauth_token')

        try:
            AUTH.get_access_token(verifier)
        except Exception as e:
            pass
        
        secret = AUTH.access_token_secret
        AUTH.set_access_token(key, secret)
        
        #Save to account
        fernet = Fernet(getKey(request.user.username))

        user = BaszlAccount.objects.get(baszlUser=request.user.username)

        if (len(user.twitteraccount_set.all()) == 0):
            __token = fernet.encrypt(key.encode())
            __timestamp = fernet.extract_timestamp(__token)
            __secret = fernet.encrypt_at_time(secret.encode(), __timestamp)
            user.twitteraccount_set.create(accessToken=__token, accessSecret=__secret, timeStamp=__timestamp, handle="", numPosts=0)
        else:
            twtAcct = TwitterAccount.objects.filter(baszlAcct=user).first()
            __token = fernet.encrypt(key.encode())
            __timestamp = fernet.extract_timestamp(__token)
            __secret = fernet.encrypt_at_time(secret.encode(), __timestamp)
            twtAcct.accessToken = __token
            twtAcct.accessSecret = __secret
            twtAcct.timeStamp = __timestamp
            twtAcct.handle = ""
            twtAcct.save()

            return HttpResponse(str(twtAcct.timeStamp))

    except Exception as e:
        pass

    return redirect("/platformsLogin/")

def makePost(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            messagePost = request.POST.get("postText")
            if messagePost:
                noPost = True
                # Get Baszl user
                user = BaszlAccount.objects.get(baszlUser=request.user.username)
                fernet = Fernet(getKey(request.user.username))

                # Something actually posted
                if request.POST.get("facebook"):
                    noPost *= False

                    # With pages_read_engagement and pages_manage_posts
                    token = 'EAAI7Mrr8DhABALiK49eaOjEsSkWbsZAWMrxXTMgxdfoGt4PzQ9oo7sVZBZAIyJs1Ky966MsGu11gZCNvUxMatdLvNsBnF6jqrc7QrCj6sjN8flf5SNU5NvXKLSQfnUZB8DApJY1FXnsMTXAQ9UXSxuYHZAoH41ZBDCPziU4ZCNKTN4FDhyxXzChR96ZBKMrz6yUicU6kVGZAFwW32fgD1TPTye'

                    fb = facebook.GraphAPI(access_token = token)
                    fb.put_object(parent_object = 'me', connection_name = 'feed', message=messagePost)

                if request.POST.get("twitter"):
                    noPost *= False
                    twtAcct = TwitterAccount.objects.filter(baszlAcct=user).first()
                    timestamp = twtAcct.timeStamp
                    print(timestamp)
                    accessToken = twtAcct.accessToken
                    key = fernet.decrypt_at_time(accessToken[2:-1].encode(), 604800, int(timestamp))
                    
                    accessSecret = twtAcct.accessSecret
                    secret = fernet.decrypt_at_time(accessSecret[2:-1].encode(), 604800, int(timestamp))

                    AUTH.set_access_token(key, secret)

                    try:
                        api=tweepy.API(AUTH)
                        api.update_status(status=messagePost)
                    except Exception as e:
                        return HttpResponse(twtAcct.__str__())

                if request.POST.get("instagram"):
                    noPost *= False

                    # Remove config folder
                    dir_path = '/config'
                    try:
                        shutil.rmtree(dir_path)
                    except OSError as e:
                        print("Error: %s : %s" % (dir_path, e.strerror))


                    #bot = Bot()

                    #try:
                    #bot.login(username = "BASZL315", password = "ptaele315")
                    #print("Logged in...")
                    #bot.upload_photo("/static/i.jpg", caption=messagePost)
                    #except Exception as e:
                        

                if noPost:
                    print("No post")
                else:
                    print(messagePost)
                    # user.account.numPosts += 1
        return redirect("/")
    else:
        return HttpResponse("You are not authorized for this activity")