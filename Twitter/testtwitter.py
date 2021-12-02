import tweepy
import webbrowser
consumer_key = '1OT7fMp7nItZHuuXNwv0duBs2'
consumer_secret = 'zUAsq7LIlNPzxPOuIvWWQ9uqGoG1YUJ12uD7qzK5obWmebViVr'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret, 'oob')
auth_url = auth.get_authorization_url()
webbrowser.open(auth_url)
token = auth.request_token['oauth_token']
verifier = input('Verifier:')
auth.get_access_token(verifier)
key = auth.access_token
secret = auth.access_token_secret

auth.set_access_token(key, secret)
api = tweepy.API(auth)
api.update_status('Success!')
