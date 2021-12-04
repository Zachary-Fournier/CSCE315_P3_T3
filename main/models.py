from django.db import models
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

class FacebookAccount(models.Model):
    baszlAcct = models.ForeignKey(BaszlAccount, on_delete=models.CASCADE)
    accessToken = models.CharField(max_length=300)
    handle = models.CharField(max_length=200,blank=True, null=True)
    numPosts = models.IntegerField(default=0)

class TwitterAccount(models.Model):
    baszlAcct = models.ForeignKey(BaszlAccount, on_delete=models.CASCADE)
    accessToken = models.CharField(max_length=300)
    accessSecret = models.CharField(max_length=300)
    timeStamp = models.IntegerField(default=0)
    handle = models.CharField(max_length=200, blank=True, null=True)
    numPosts = models.IntegerField(default=0)

    def __str__(self):
        string = "Access Token: " + self.accessToken + "\n"
        string += "Access Secret: " + self.accessSecret + "\n"
        string += "Timestamp: " + str(self.timeStamp)

        return string