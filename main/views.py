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
import threading
import asyncio
from async_timeout import timeout
import copy

sessionDict = {}

def getKey(string):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt= b',\x1b%\xb2\xc8\xd1\xedBL\xf1\x1er8\xc1\xf6V',
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(string.encode()))

def makePostThread(request, sessionKey):
    # Get Baszl user and session info
    user = BaszlAccount.objects.get(baszlUser=request.user.username)
    fernet = Fernet(getKey(request.user.username))
    keyCopy = copy.deepcopy(sessionKey)
    sessionInfo = sessionDict[sessionKey]
    sessionDict[sessionKey]['fetched'] = 1  # free to go back

    if sessionInfo['imagePath'] or sessionInfo['postText']:
        errorCodes = ["", "", ""]

        # Something actually posted
        if sessionInfo['fb']:
            fbAcct = FacebookAccount.objects.filter(baszlAcct=user).first()
            timestamp = fbAcct.timeStamp
            pageToken = fbAcct.pageToken
            pageToken = fernet.decrypt_at_time(pageToken[2:-1].encode(), 604800, int(timestamp)).decode()

            if sessionInfo['imagePath']:
                try:
                    fb = facebook.GraphAPI(access_token=pageToken)
                    fb.put_photo(image=open(sessionInfo['imagePath'], 'rb'), message=sessionInfo['postText'])
                    fbAcct.numPosts = fbAcct.numPosts + 1
                    fbAcct.save()
                except Exception as e:
                    errorCodes[0] = "420"

            else:
                try:
                    fb = facebook.GraphAPI(access_token=pageToken)
                    fb.put_object(parent_object='me', connection_name='feed', message=sessionInfo['postText'])
                    fbAcct.numPosts = fbAcct.numPosts + 1
                    fbAcct.save()
                except Exception as e:
                    errorCodes[0] = "420"

        if sessionInfo['twt']:
            twtAcct = TwitterAccount.objects.filter(baszlAcct=user).first()
            timestamp = twtAcct.timeStamp
            accessToken = twtAcct.accessToken
            key = fernet.decrypt_at_time(accessToken[2:-1].encode(), 604800, int(timestamp)).decode()
            
            accessSecret = twtAcct.accessSecret
            secret = fernet.decrypt_at_time(accessSecret[2:-1].encode(), 604800, int(timestamp)).decode()

            auth = tweepy.OAuthHandler(consumer_key, consumer_secret, 'https://baszl.herokuapp.com/twitteraccess/')
            auth.set_access_token(key, secret)

            if sessionInfo['imagePath']:
                try:
                    api=tweepy.API(auth)

                    # Upload picture and get postId for media
                    media = api.media_upload(sessionInfo['imagePath'])
                    idList = list()
                    idList.append(media.media_id)

                    # Update status and associate the previously posted media
                    api.update_status(status=sessionInfo['postText'], media_ids=idList)

                    twtAcct.numPosts = twtAcct.numPosts + 1
                    twtAcct.save()
                except Exception as e:
                    errorCodes[1] = "421"

            else:
                # Standard Tweet
                try:
                    api=tweepy.API(auth)
                    api.update_status(status=sessionInfo['postText'])
                    twtAcct.numPosts = twtAcct.numPosts + 1
                    twtAcct.save()
                except Exception as e:
                    errorCodes[1] = "421"

                twtAcct.numPosts = twtAcct.numPosts + 1
                twtAcct.save()

        if sessionInfo['ig']:
            # Remove config folder if left behind
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
            if sessionInfo['imagePath']:
                imagePath = sessionInfo['imagePath']

            bot.login(username=__username, password=__password, force=True, is_threaded=True)
            try:
                bot.upload_photo(imagePath, caption=sessionInfo['postText'])
            except Exception as e:
                pass
            
            # Clean up
            try:
                shutil.rmtree(dir_path)
            except OSError as e:
                errorCodes[2] = "422"

            if not sessionInfo['imagePath']:
                try:
                    os.rename(imagePath + ".REMOVE_ME", imagePath)
                except OSError as e:
                    errorCodes[2] = "422"
        
        # Remove image if it exists
        if sessionInfo['imagePath']:
            try:
                os.remove(sessionInfo['imagePath'])
            except OSError as e:
                errorCodes[2] = "418"
        
        # Update any errors
        errorString = user.statusCodes.split(",")
        for code in errorCodes:
            if code:
                errorString += "," + code

        user.statusCodes = errorString
        user.save()

    del sessionDict[keyCopy]

async def postAwaitable(request, sessionKey):
    postThread = threading.Thread(target=makePostThread, args=(request, sessionKey,))
    postThread.start()

async def postTimeoutWrapper(request, sessionKey):
    # Timeout after a minute
    async with timeout(60) as contextManager:
        await postAwaitable(request, sessionKey)
    if contextManager.expired:
        user = BaszlAccount.objects.get(baszlUser=request.user.username)
        user.statusCodes = user.statusCodes + ",423"

consumer_key = '1OT7fMp7nItZHuuXNwv0duBs2'
consumer_secret = 'zUAsq7LIlNPzxPOuIvWWQ9uqGoG1YUJ12uD7qzK5obWmebViVr'

# Create your views here.
def home(request):
    twtHandle=igHandle=fbHandle = "Not Connected"
    fbPosts=igPosts=twtPosts = 0

    if not request.user.is_authenticated:
        return HttpResponseRedirect("/login/")

    user = BaszlAccount.objects.get(baszlUser=request.user.username)
    baszlHandle = user.baszlUser

    statusCodes = user.statusCodes
    codes = statusCodes.split(",")
    numErrors = 0
    for code in codes:
        if code:
            if code[0] == "4":
                numErrors += 1
    # Reset codes
    user.statusCodes = ""
    user.save()

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
    return render(request, "main/dashboard.html", {"iform":iform, "baszlHandle":baszlHandle, "twtHandle":twtHandle, "igHandle":igHandle, "fbHandle":fbHandle, "numFbPosts":fbPosts, "numIgPosts":igPosts, "numTwtPosts":twtPosts, "numErrors":numErrors})
        
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

    user = BaszlAccount.objects.get(baszlUser=request.user.username)
    sessionKey = base64.urlsafe_b64encode(os.urandom(16)).decode()
    sessionDict[sessionKey] = {"fetched": 0,"imagePath":"", "postText":"", "fb":False, "twt":False, "ig":False}

    if request.POST.get("facebook"):
        sessionDict[sessionKey]['fb'] = True
    if request.POST.get("twitter"):
        sessionDict[sessionKey]['twt'] = True
    if request.POST.get("instagram"):
        sessionDict[sessionKey]['ig'] = True

    if request.FILES:
        iform = ImageForm(request.POST.get('img'), request.FILES)
        if iform.is_valid():
            image_field = iform.cleaned_data['img']
            image = Image.open(image_field)
            filename = base64.urlsafe_b64encode(os.urandom(8)).decode() + "." + image.format

            imagePath = BASE_DIR + "/uploads/" + filename
            image.save(imagePath, image.format)

            sessionDict[sessionKey]['imagePath'] = imagePath
        else:
            user.statusCodes = user.statusCodes + ",419"

    if request.POST.get("postText"):
        sessionDict[sessionKey]['postText'] = request.POST.get("postText")

    if request.method == "POST":
        asyncio.run(postTimeoutWrapper(request, sessionKey))

    while sessionDict[sessionKey]['fetched'] == 0:
        continue

    return redirect("/")