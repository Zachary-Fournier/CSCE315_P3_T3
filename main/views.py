from logging import error
from django.db import reset_queries
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
import tweepy
import facebook 
from instabot import Bot
from .models import *
import shutil
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from project3_backend.settings import BASE_DIR
from .forms import ImageForm
from PIL import Image
import os
from django.core.files.uploadedfile import SimpleUploadedFile

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
def home(request):
    twtHandle=igHandle=fbHandle = "Not Connected"
    fbPosts=igPosts=twtPosts = 0

    if not request.user.is_authenticated:
        return HttpResponseRedirect("/login/")

    user = BaszlAccount.objects.get(baszlUser=request.user.username)
    try:
        fbAcct = FacebookAccount.objects.filter(baszlAcct=user).first()
        fbHandle = fbAcct.handle
        fbPosts = fbAcct.numPosts
    except Exception as e:
        pass
    try:
        twtAcct = TwitterAccount.objects.filter(baszlAcct=user).first()
        twtHandle = twtAcct.handle
        twtPosts = twtAcct.numPosts
    except Exception as e:
        pass
    try:
        igAcct = InstagramAccount.objects.filter(baszlAcct=user).first()
        igHandle = igAcct.username
        igPosts = igAcct.numPosts
    except Exception as e:
        pass

    iform = ImageForm()
    return render(request, "main/dashboard.html", {"iform":iform, "twtHandle":twtHandle, "igHandle":igHandle, "fbHandle":fbHandle, "numFbPosts":fbPosts, "numIgPosts":igPosts, "numTwtPosts":twtPosts})
        
def platformsLogin(request):
    if not request.user.is_authenticated:
        return redirect("/login/")

    return render(request, "main/platformsLogin.html", {})

def getFacebookToken(request, info):
    if not request.user.is_authenticated:
        return redirect("/login/")

    response = info.split("&")
    token = response[0]
    __pageToken = response[1]
    __pageID = response[2]
    name = response[3]
    
    # Save to account
    try:
        user = BaszlAccount.objects.get(baszlUser=request.user.username)
        fernet = Fernet(getKey(request.user.username))

        if (len(user.facebookaccount_set.all()) == 0):
            __token = fernet.encrypt(token.encode())
            __timestamp = fernet.extract_timestamp(__token)
            __pageToken = fernet.encrypt_at_time(__pageToken.encode(), __timestamp)
            __pageID = fernet.encrypt_at_time(__pageID.encode(), __timestamp)
            user.facebookaccount_set.create(accessToken=__token, pageToken=__pageToken, pageID=__pageID, timeStamp=__timestamp, handle=name, numPosts=0)
        else:
            fbAcct = FacebookAccount.objects.filter(baszlAcct=user).first()
            __token = fernet.encrypt(token.encode())
            __timestamp = fernet.extract_timestamp(__token)
            __pageToken = fernet.encrypt_at_time(__pageToken.encode(), __timestamp)
            __pageID = fernet.encrypt_at_time(__pageID.encode(), __timestamp)
            fbAcct.accessToken = __token
            fbAcct.pageToken = __pageToken
            fbAcct.pageID = __pageID
            fbAcct.timeStamp = __timestamp
            fbAcct.handle = name
            fbAcct.save()

        return redirect("/platformsLogin/")
    except Exception as e:
        #return HttpResponse(fbAcct.__str__())
        return render(request, "main/accessError.html", {"platform":"Facebook", "msg":"Couldn't save token."})

def getTwitterToken(request):
    if not request.user.is_authenticated:
        return redirect("/login/")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, 'https://baszl.herokuapp.com/twitteraccess/')
    try:
        return redirect(auth.get_authorization_url())

    except Exception as e:
        return render(request, "main/accessError.html", {"platform":"Twitter", "msg":"Couldn't get request token."})

def getTwitterAccess(request):
    if not request.user.is_authenticated:
        return redirect("/login/")

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
    __handle = ""
    try:
        api=tweepy.API(auth)
        twtUser = api.verify_credentials()
        __handle = "@" + twtUser.screen_name
    except Exception as e:
        return render(request, "main/accessError.html", {"platform":"Twitter", "msg":"Could not get handle."})
    
    #Save to account
    try:
        fernet = Fernet(getKey(request.user.username))
        user = BaszlAccount.objects.get(baszlUser=request.user.username)

        if (len(user.twitteraccount_set.all()) == 0):
            __token = fernet.encrypt(key.encode())
            __timestamp = fernet.extract_timestamp(__token)
            __secret = fernet.encrypt_at_time(secret.encode(), __timestamp)
            user.twitteraccount_set.create(accessToken=__token, accessSecret=__secret, timeStamp=__timestamp, handle=__handle, numPosts=0)
        else:
            twtAcct = TwitterAccount.objects.filter(baszlAcct=user).first()
            __token = fernet.encrypt(key.encode())
            __timestamp = fernet.extract_timestamp(__token)
            __secret = fernet.encrypt_at_time(secret.encode(), __timestamp)
            twtAcct.accessToken = __token
            twtAcct.accessSecret = __secret
            twtAcct.timeStamp = __timestamp
            twtAcct.handle = __handle
            twtAcct.save()

    except Exception as e:
        return render(request, "main/accessError.html", {"platform":"Twitter", "msg":"Could not save credentials."})

    return redirect("/platformsLogin/")

def getInstagramAccess(request):
    if not request.user.is_authenticated:
        return redirect("/login/")

    if request.method == "POST":
        __username = request.POST.get("uname")
        __password = request.POST.get("psw")

        #Save to account
        try:
            fernet = Fernet(getKey(request.user.username))
            user = BaszlAccount.objects.get(baszlUser=request.user.username)

            if (len(user.instagramaccount_set.all()) == 0):
                __password = fernet.encrypt(__password.encode())
                __timestamp = fernet.extract_timestamp(__password)
                user.instagramaccount_set.create(username=__username, password=__password, timeStamp=__timestamp, numPosts=0)
            else:
                igAcct = InstagramAccount.objects.filter(baszlAcct=user).first()
                __password = fernet.encrypt(__password.encode())
                __timestamp = fernet.extract_timestamp(__password)
                igAcct.username = __username
                igAcct.password = __password
                igAcct.timeStamp = __timestamp
                igAcct.save()
            
        except Exception as e:
            return render(request, "main/accessError.html", {"platform":"Instagram", "msg":"Could not save credentials."})

        return redirect("/platformsLogin/")

def makePost(request):
    if not request.user.is_authenticated:
        return redirect("/login/")
    
    if request.method == "POST":
        postImage = False
        postMessage = False
        messagePost = None
        iform = None
        if request.FILES:
            postImage = True
            iform = ImageForm(request.POST.get('img'), request.FILES)
        if request.POST.get("postText"):
            postMessage = True
            messagePost = request.POST.get("postText")

        if postMessage or postImage:
            noPost = True
            # Get Baszl user
            user = BaszlAccount.objects.get(baszlUser=request.user.username)
            fernet = Fernet(getKey(request.user.username))

            # Something actually posted
            if request.POST.get("facebook"):
                fbAcct = FacebookAccount.objects.filter(baszlAcct=user).first()
                timestamp = fbAcct.timeStamp
                pageToken = fbAcct.pageToken
                pageToken = fernet.decrypt_at_time(pageToken[2:-1].encode(), 604800, int(timestamp)).decode()

                try:
                    fb = facebook.GraphAPI(access_token=pageToken)
                    fb.put_object(parent_object='me', connection_name='feed', message=messagePost)
                    fbAcct.numPosts = fbAcct.numPosts + 1
                    fbAcct.save()
                except Exception as e:
                    return HttpResponse("<p>Error posting to Facebook. Click <a href=\"/\">here</a> to return</p>")

            if request.POST.get("twitter"):
                twtAcct = TwitterAccount.objects.filter(baszlAcct=user).first()
                timestamp = twtAcct.timeStamp
                accessToken = twtAcct.accessToken
                key = fernet.decrypt_at_time(accessToken[2:-1].encode(), 604800, int(timestamp)).decode()
                
                accessSecret = twtAcct.accessSecret
                secret = fernet.decrypt_at_time(accessSecret[2:-1].encode(), 604800, int(timestamp)).decode()

                auth = tweepy.OAuthHandler(consumer_key, consumer_secret, 'https://baszl.herokuapp.com/twitteraccess/')
                auth.set_access_token(key, secret)

                if postImage:
                    imagePath = BASE_DIR + "/uploads/"
                    if iform.is_valid():
                        image_field = iform.cleaned_data['img']
                        image = Image.open(image_field)
                        filename = base64.urlsafe_b64encode(os.urandom(8)).decode() + "." + image.format

                        imagePath += filename
                        image.save(imagePath, image.format)
                    else:
                        return HttpResponse("<p>Error getting image. Click <a href=\"/\">here</a> to return.</p>")

                    #try:
                    api=tweepy.API(auth)

                    # Upload picture and get postId for media
                    media = api.media_upload(imagePath)
                    idList = ()
                    idList.append(media.media_id)

                    # Update status and associate the previously posted media
                    api.update_status(status=messagePost, media_ids=idList)

                    twtAcct.numPosts = twtAcct.numPosts + 1
                    twtAcct.save()
                    #except Exception as e:
                        #return HttpResponse("<p>Error posting to Twitter. Click <a href=\"/\">here</a> to return</p>" + str(media.media_id))

                    # Clean up
                    try:
                        os.remove(imagePath)
                    except OSError as e:
                        return HttpResponse("<p>Error deleting config folder.</p>")

                else:
                    # Standard Tweet
                    try:
                        api=tweepy.API(auth)
                        api.update_status(status=messagePost)
                        twtAcct.numPosts = twtAcct.numPosts + 1
                        twtAcct.save()
                    except Exception as e:
                        return HttpResponse("<p>Error posting to Twitter. Click <a href=\"/\">here</a> to return</p>")

                    twtAcct.numPosts = twtAcct.numPosts + 1
                    twtAcct.save()

            if request.POST.get("instagram"):
                # Remove config folder
                dir_path = BASE_DIR + "/config/"
                try:
                    shutil.rmtree(dir_path)
                except OSError as e:
                    pass

                # Can't use try/except
                bot = Bot()
                igAcct = InstagramAccount.objects.filter(baszlAcct=user).first()
                timestamp = igAcct.timeStamp
                __password = igAcct.password
                __password = fernet.decrypt_at_time(__password[2:-1].encode(), 604800, int(timestamp)).decode()
                __username = igAcct.username

                imagePath = BASE_DIR + "/uploads/baszl.jpg"
                if postImage:
                    if iform.is_valid():
                        image_field = iform.cleaned_data['img']
                        image = Image.open(image_field)
                        filename = base64.urlsafe_b64encode(os.urandom(8)).decode() + "." + image.format

                        imagePath = BASE_DIR + "/uploads/" + filename
                        image.save(imagePath, image.format)
                    else:
                        return HttpResponse("<p>Error getting image. Click <a href=\"/\">here</a> to return.</p>")

                bot.login(username=__username, password=__password, is_threaded=True)
                bot.upload_photo(imagePath, caption=messagePost)

                # Clean up
                errorMsg = ""
                try:
                    shutil.rmtree(dir_path)
                except OSError as e:
                    errorMsg = "<p>Error deleting config folder.</p>"

                if postImage:
                    try:
                        os.remove(imagePath)
                    except OSError as e:
                        errorMsg += "<p>Error deleting uploaded image.</p>"
                else:
                    try:
                        os.rename(imagePath + ".REMOVE_ME", imagePath)
                    except OSError as e:
                        errorMsg += "<p>Error renaming default image</p>"
                
                if errorMsg:
                    errorMsg += "<p>Click <a href=\"/\">here</a> to return.</p>"
                    return HttpResponse(errorMsg)

    return redirect("/")

def test(request):
    if request.method == "POST":
        print(request.POST)
        chk = request.POST.get('chk')
        print(chk)
        if request.FILES:
            iform = ImageForm(request.POST.get('img'), request.FILES)
            if iform.is_valid():
                image_field = iform.cleaned_data['img']
                image = Image.open(image_field)

                print("Saving...")
                print(BASE_DIR + "\static\imgToPost." + image.format.lower())
                image.save(BASE_DIR + "\static\imgToPost." + image.format, image.format)

        return redirect("/test/")
            
    else:
        iform = ImageForm()

        return render(request, "main/test.html", {"iform":iform})