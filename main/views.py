from logging import error
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from allauth.socialaccount.models import SocialToken
from django.contrib.auth.models import User
import tweepy
import facebook 
from instabot import Bot
from .models import BaszlAccount

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
        #
        x = 1

    return render(request, "main/platformsLogin.html", {})

def getFacebookToken(request, token):
    return HttpResponse(token)
    #return redirect("/platformsLogin/")

def getTwitterToken(request):
    return redirect(AUTH.get_authorization_url())

def getTwitterAccess(request):
    verifier = request.GET.get('oauth_verifier')
    AUTH.get_access_token(verifier)
    key = AUTH.access_token
    secret = AUTH.access_token_secret
    AUTH.set_access_token(key, secret)

    return redirect("/platformsLogin/")

def makePost(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            username = request.user.username
            messagePost = request.POST.get("postText")
            if messagePost:
                noPost = True
                # Something actually posted
                if request.POST.get("facebook"):
                    noPost *= False

                    # With pages_read_engagement and pages_manage_posts
                    token = 'EAAI7Mrr8DhABALiK49eaOjEsSkWbsZAWMrxXTMgxdfoGt4PzQ9oo7sVZBZAIyJs1Ky966MsGu11gZCNvUxMatdLvNsBnF6jqrc7QrCj6sjN8flf5SNU5NvXKLSQfnUZB8DApJY1FXnsMTXAQ9UXSxuYHZAoH41ZBDCPziU4ZCNKTN4FDhyxXzChR96ZBKMrz6yUicU6kVGZAFwW32fgD1TPTye'

                    fb = facebook.GraphAPI(access_token = token)
                    fb.put_object(parent_object = 'me', connection_name = 'feed', message=messagePost)

                if request.POST.get("twitter"):
                    noPost *= False

                    api=tweepy.API(AUTH)
                    api.update_status(status=messagePost)

                if request.POST.get("instagram"):
                    noPost *= False

                    bot = Bot()

                    try:
                        bot.login(username = "BASZL315", password = "ptaele315")
                        bot.upload_photo("../static/i.jpg", caption=messagePost)
                    except Exception as e:
                        print(e.__context__)

                if noPost:
                    print("No post")
                else:
                    print(messagePost)
                    # user.account.numPosts += 1
        return redirect("/")
    else:
        return HttpResponse("You are not authorized for this activity")