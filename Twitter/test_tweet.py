from django.shortcuts import redirect
import numpy as np
import tweepy

consumer_key = '1OT7fMp7nItZHuuXNwv0duBs2'
consumer_secret_key = 'zUAsq7LIlNPzxPOuIvWWQ9uqGoG1YUJ12uD7qzK5obWmebViVr' 

access_token = '1455922761499652099-sYxiuHGXfDQrBgRiWalCNbS5FcFpjI'
access_secret_token = '9CjvignMJyKWJUHJvrNyXTzOnUsOgQNhbD9y8G9rQeq6q'

auth = tweepy.OAuthHandler(consumer_key,consumer_secret_key)

try: 
    redirect_url = auth.get_authorization_url()
except tweepy.TweepError:
    print("Error getting token")
    
auth.set_access_token(access_token,access_secret_token)
api=tweepy.API(auth)

tweet=input('Enter your tweet: ')
api.update_status(status=tweet)