from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
import tweepy
import facebook
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
import requests
import json

sessionDict = {}

def getKey(string):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt= b',\x1b%\xb2\xc8\xd1\xedBL\xf1\x1er8\xc1\xf6V',
        iterations=390000,
    )
    return base64.urlsafe_b64encode(kdf.derive(string.encode()))

def getPhoto(request):
    response = None
    if request.method == "GET":
        filename = request.GET.get('filename')
        imagePath = BASE_DIR + "/uploads/" + filename
        response = HttpResponse(open(imagePath, "rb"), headers={
            'Content-Type': 'image/jpeg',
            'Content-Length': os.path.getsize(imagePath),
            'Content-Disposition': 'attachment; filename=' + filename,
        })
    try:
        if filename != "baszl.jpg":
            os.remove(imagePath)
    except OSError as e:
        pass

    return response

def makePostThread(request, sessionKey):
    # Get Baszl user and session info
    user = BaszlAccount.objects.get(baszlUser=request.user.username)
    fernet = Fernet(getKey(request.user.username))
    keyCopy = copy.deepcopy(sessionKey)
    sessionInfo = sessionDict[sessionKey]
    sessionDict[sessionKey]['fetched'] = 1  # free to go back

    if sessionInfo['filename'] or sessionInfo['postText']:
        errorCodes = ["", "", ""]

        # Something actually posted
        if sessionInfo['fb']:
            fbAcct = FacebookAccount.objects.filter(baszlAcct=user).first()
            # Check if account set up
            if not fbAcct:
                print("No account")
                return
            timestamp = fbAcct.timeStamp
            pageToken = fbAcct.pageToken
            pageToken = fernet.decrypt_at_time(pageToken[2:-1].encode(), 604800, int(timestamp)).decode()

            if sessionInfo['filename']:
                try:
                    fb = facebook.GraphAPI(access_token=pageToken)
                    fb.put_photo(image=open(BASE_DIR + "/uploads/" + sessionInfo['filename'], 'rb'), message=sessionInfo['postText'])
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
            # Check if account set up
            if not twtAcct:
                print("No account")
                return
            timestamp = twtAcct.timeStamp
            accessToken = twtAcct.accessToken
            key = fernet.decrypt_at_time(accessToken[2:-1].encode(), 604800, int(timestamp)).decode()
            
            accessSecret = twtAcct.accessSecret
            secret = fernet.decrypt_at_time(accessSecret[2:-1].encode(), 604800, int(timestamp)).decode()

            auth = tweepy.OAuthHandler(consumer_key, consumer_secret, 'https://baszl.herokuapp.com/twitteraccess/')
            auth.set_access_token(key, secret)

            if sessionInfo['filename']:
                try:
                    api=tweepy.API(auth)

                    # Upload picture and get postId for media
                    media = api.media_upload(BASE_DIR + "/uploads/" + sessionInfo['filename'])
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

        if sessionInfo['ig']:
            # Get user access token and ig ID
            fbAcct = FacebookAccount.objects.filter(baszlAcct=user).first()
            # Check if account set up
            if not fbAcct:
                print("No account")
                return
            timestamp = fbAcct.timeStamp
            accessToken = fbAcct.accessToken
            accessToken = fernet.decrypt_at_time(accessToken[2:-1].encode(), 604800, int(timestamp)).decode()

            igAcct = InstagramAccount.objects.filter(baszlAcct=user).first()
            # Check if account set up
            if not igAcct:
                print("No account")
                return
            timestamp = igAcct.timeStamp
            __igID = igAcct.accountID
            __igID = fernet.decrypt_at_time(__igID[2:-1].encode(), 604800, int(timestamp)).decode()
            
            #__igID = 17841450558552750

            imagePath = BASE_DIR + "/uploads/"
            filename = "baszl.jpg"
            if sessionInfo['filename']:
                filename = sessionInfo['filename']
            imagePath += filename

            try:
                # Upload pictur to media container
                apiUrl = 'https://graph.facebook.com/v12.0/' + __igID
                imageUrl = 'https://baszl.herokuapp.com/getPhoto?filename=' + filename
                payload = {
                    'image_url': imageUrl,
                    'caption': sessionInfo['postText'],
                    'access_token': accessToken
                }
                r = requests.post(apiUrl + '/media', data=payload)

                # Publish upload
                result = json.loads(r.text)
                if 'id' in result:
                    containerID = result['id']
                    second_payload = {
                        'creation_id': containerID,
                        'access_token': accessToken
                    }
                    r = requests.post(apiUrl + '/media_publish', data=second_payload)

                # Track progress
                igAcct.numPosts = igAcct.numPosts + 1
                igAcct.save()
            except Exception as e:
                pass
        
        # Remove image if it exists for Facebook and Twitter
        if sessionInfo['filename'] and not sessionInfo['ig']:
            try:
                os.remove(sessionInfo['filename'])
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
        igHandle = igAcct.handle
        igPosts = igAcct.numPosts
    except Exception as e:
        pass

    iform = ImageForm()
    return render(request, "main/dashboard.html", {"iform":iform, "baszlHandle":baszlHandle, "twtHandle":twtHandle, "igHandle":igHandle, "fbHandle":fbHandle, "numFbPosts":fbPosts, "numIgPosts":igPosts, "numTwtPosts":twtPosts, "numErrors":numErrors})
        
def platformsLogin(request):
    if not request.user.is_authenticated:
        return redirect("/login/")

    return render(request, "main/platformsLogin.html", {})

def getFbandIGAccess(request):
    if not request.user.is_authenticated:
        return redirect("/login/")

    token = request.GET.get('user_access_token') # Fb
    __pageToken = request.GET.get('page_access_token') # Fb
    __pageID = request.GET.get('page_id') # Fb
    __igID = request.GET.get('instagram_id')
    __igHandle = request.GET.get('instagram_username')
    name = request.GET.get('name') # Fb
    
    # Save to Facebook account
    user = BaszlAccount.objects.get(baszlUser=request.user.username)
    fernet = Fernet(getKey(request.user.username))
    try:
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

    except Exception as e:
        #return HttpResponse(fbAcct.__str__())
        return render(request, "main/accessError.html", {"platform":"Facebook", "msg":"Couldn't save token."})

    #Save to Instagram account
    try:
        if (len(user.instagramaccount_set.all()) == 0):
            __igID = fernet.encrypt(__igID.encode())
            __timestamp = fernet.extract_timestamp(__igID)
            user.instagramaccount_set.create(accountID=__igID, timeStamp=__timestamp, handle=__igHandle, numPosts=0)
        else:
            igAcct = InstagramAccount.objects.filter(baszlAcct=user).first()
            __igID = fernet.encrypt(__igID.encode())
            __timestamp = fernet.extract_timestamp(__igID)
            igAcct.accountID = __igID
            igAcct.timeStamp = __timestamp
            igAcct.handle = __igHandle
            igAcct.save()
        
    except Exception as e:
        return render(request, "main/accessError.html", {"platform":"Instagram", "msg":"Could not save credentials."})

    return redirect("/platformsLogin/")

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

def makePost(request):
    if not request.user.is_authenticated:
        return redirect("/login/")

    user = BaszlAccount.objects.get(baszlUser=request.user.username)
    sessionKey = base64.urlsafe_b64encode(os.urandom(16)).decode()
    sessionDict[sessionKey] = {"fetched": 0,"filename":"", "postText":"", "fb":False, "twt":False, "ig":False}

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
            image = image.convert('RGB')
            filename = base64.urlsafe_b64encode(os.urandom(8)).decode() + ".JPEG"

            imagePath = BASE_DIR + "/uploads/" + filename
            image.save(imagePath, image.format)

            sessionDict[sessionKey]['filename'] = filename
        else:
            user.statusCodes = user.statusCodes + ",419"

    if request.POST.get("postText"):
        sessionDict[sessionKey]['postText'] = request.POST.get("postText")

    if request.method == "POST":
        asyncio.run(postTimeoutWrapper(request, sessionKey))

    while sessionDict[sessionKey]['fetched'] == 0:
        continue

    return redirect("/")