from django.db import models
from cryptography.fernet import Fernet
import tweepy

# Create your models here.

class BaszlAccount(models.Model):
    baszlUser = models.CharField(max_length=200)

class InstagramAccount(models.Model):
    baszlAcct = models.ForeignKey(BaszlAccount, on_delete=models.CASCADE)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    handle = models.CharField(max_length=200, blank=True, null=True)
    numPosts = models.IntegerField(default=0)
    fernet = Fernet(Fernet.generate_key())

    def setPassword(self, __password):
        self.password = self.fernet.encrypt(__password.encode())
        return

    def getPassword(self):
        return self.fernet.decrypt(self.password).decode()

    def __init__(self, __username, __password):
        self.username = __username
        self.setPassword(__password)

class FacebookAccount(models.Model):
    baszlAcct = models.ForeignKey(BaszlAccount, on_delete=models.CASCADE)
    accessToken = models.CharField(max_length=300)
    handle = models.CharField(max_length=200,blank=True, null=True)
    numPosts = models.IntegerField(default=0)
    fernet = Fernet(Fernet.generate_key())

    def setToken(self, __token):
        self.accessToken = self.fernet.encrypt(__token.encode())
        return

    def getToken(self):
        return self.fernet.decrypt(self.accessToken).decode()

    def __init__(self, __token):
        self.setToken(__token)

class TwitterAccount(models.Model):
    baszlAcct = models.ForeignKey(BaszlAccount, on_delete=models.CASCADE)
    accessToken = models.CharField(max_length=300)
    accessSecret = models.CharField(max_length=300)
    handle = models.CharField(max_length=200, blank=True, null=True)
    numPosts = models.IntegerField(default=0)
    fernet = Fernet(Fernet.generate_key())

    def setToken(self, __token):
        self.accessToken = self.fernet.encrypt(__token.encode())
        return

    def getToken(self):
        return self.fernet.decrypt(self.accessToken).decode()

    def setSecret(self, __secret):
        self.accessSecret = self.fernet.encrypt(__secret.encode())
        return

    def getSecret(self):
        return self.fernet.decrypt(self.accessSecret).decode()

    def __init__(self, __token, __secret):
        self.setToken(__token)
        self.setSecret(__secret)