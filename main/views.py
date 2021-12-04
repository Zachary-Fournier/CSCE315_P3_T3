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
    try:
        user = BaszlAccount.objects.get(baszlUser=request.user.username)
        fernet = Fernet(getKey(request.user.username))

        if (len(user.facebookaccount_set.all()) == 0):
            __token = fernet.encrypt(token.encode())
            __timestamp = fernet.extract_timestamp(__token)
            user.facebookaccount_set.create(accessToken=__token, timeStamp=__timestamp, handle="", numPosts=0)
        else:
            fbAcct = FacebookAccount.objects.filter(baszlAcct=user).first()
            __token = fernet.encrypt(token.encode())
            __timestamp = fernet.extract_timestamp(__token)
            fbAcct.accessToken = __token
            fbAcct.timeStamp = __timestamp
            fbAcct.handle = ""
            fbAcct.save()

        return redirect("/platformsLogin/")
    except Exception as e:
        return render(request, "main/accessError.html", {"platform":"Facebook", "msg":"Couldn't save token."})

def getTwitterToken(request):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, 'https://baszl.herokuapp.com/twitteraccess/')
    try:
        return redirect(auth.get_authorization_url())

    except Exception as e:
        return render(request, "main/accessError.html", {"platform":"Twitter", "msg":"Couldn't get request token."})

def getTwitterAccess(request):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, 'https://baszl.herokuapp.com/twitteraccess/')
    verifier = request.GET.get('oauth_verifier')
    token = request.GET.get('oauth_token')
    auth.request_token = {
        'oauth_token':token,
        'oauth_token_secret':verifier
    }

    try:
        auth.get_access_token(verifier)
    except Exception as e:
        return render(request, "main/accessError.html", {"platform":"Twitter", "msg":"Could not get access token."})
        
    key = auth.access_token
    secret = auth.access_token_secret
    #auth.set_access_token(key, secret)

    #return HttpResponse("<p>" + key + "</p><p>" + secret + "</p>")
    
    #Save to account
    try:
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

    except Exception as e:
        return render(request, "main/accessError.html", {"platform":"Twitter", "msg":"Could not save credentials."})

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

                    fbAcct = FacebookAccount.objects.filter(baszlAcct=user).first()
                    timestamp = fbAcct.timeStamp
                    accessToken = fbAcct.accessToken
                    key = fernet.decrypt_at_time(accessToken[2:-1].encode(), 604800, int(timestamp)).decode()

                    # With pages_read_engagement and pages_manage_posts
                    token = 'EAAI7Mrr8DhABALiK49eaOjEsSkWbsZAWMrxXTMgxdfoGt4PzQ9oo7sVZBZAIyJs1Ky966MsGu11gZCNvUxMatdLvNsBnF6jqrc7QrCj6sjN8flf5SNU5NvXKLSQfnUZB8DApJY1FXnsMTXAQ9UXSxuYHZAoH41ZBDCPziU4ZCNKTN4FDhyxXzChR96ZBKMrz6yUicU6kVGZAFwW32fgD1TPTye'

                    try:
                        fb = facebook.GraphAPI(access_token=key)
                        fb.put_object(parent_object='me', connection_name='feed', message=messagePost)
                    except Exception as e:
                        return HttpResponse("<p>Error posting to Facebook. Click <a href=\"/\">here</a> to return</p>")

                if request.POST.get("twitter"):
                    noPost *= False
                    twtAcct = TwitterAccount.objects.filter(baszlAcct=user).first()
                    timestamp = twtAcct.timeStamp
                    accessToken = twtAcct.accessToken
                    key = fernet.decrypt_at_time(accessToken[2:-1].encode(), 604800, int(timestamp)).decode()
                    
                    accessSecret = twtAcct.accessSecret
                    secret = fernet.decrypt_at_time(accessSecret[2:-1].encode(), 604800, int(timestamp)).decode()

                    #key = "1461016776800718857-t2pUgaCncOZn4UG0BsU4kiyYAkOb2O"
                    #secret = "y4EbIWd5sDCKiPvgCz0XT8zaxDaygmPX3WyNWCl9ifwIt"
                    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, 'https://baszl.herokuapp.com/twitteraccess/')
                    auth.set_access_token(key, secret)

                    try:
                        api=tweepy.API(auth)
                        api.update_status(status=messagePost)
                    except Exception as e:
                        return HttpResponse("<p>" + key + "</p><p>" + secret + "</p>")

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