from django.db import models
from cryptography.fernet import Fernet

# Create your models here.

class ToDoList(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class Item(models.Model):
    todolist = models.ForeignKey(ToDoList, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    complete = models.BooleanField()

    def __str__(self):
        return self.text

class InstagramAccount(models.Model):
    username = models.CharField(max_length=200)
    handle = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    fernet = Fernet(Fernet.generate_key())
    numPosts = models.IntegerField()

    def setPassword(self, __password):
        self.password = self.fernet.encrypt(__password.encode())
        return

    def getPassword(self):
        return self.fernet.decrypt(self.password).decode()

class FacebookAccount(models.Model):
    accessToken = models.CharField(max_length=300)
    fernet = Fernet(Fernet.generate_key())
    handle = models.CharField(max_length=200)
    numPosts = models.IntegerField()

    def setToken(self, __token):
        self.accessToken = self.fernet.encrypt(__token.encode())
        return

    def getToken(self):
        return self.fernet.decrypt(self.accessToken).decode()

class TwitterAccount(models.Model):
    accessToken = models.CharField(max_length=300)
    accessSecretToken = models.CharField(max_length=300)
    fernet = Fernet(Fernet.generate_key())
    handle = models.CharField(max_length=200)
    numPosts = models.IntegerField()

    def setToken(self, __token):
        self.accessToken = self.fernet.encrypt(__token.encode())
        return

    def getToken(self):
        return self.fernet.decrypt(self.accessToken).decode()

    def setSecretToken(self, __secretToken):
        self.accessSecretToken = self.fernet.encrypt(__secretToken.encode())
        return

    def getSecretToken(self):
        return self.fernet.decrypt(self.accessSecretToken).decode()


class BaszlAccount(models.Model):
    baszlUser = models.CharField(max_length=200)
    twitterAccount = models.ForeignKey(TwitterAccount, on_delete=models.CASCADE)
    facebookAccount = models.ForeignKey(FacebookAccount, on_delete=models.CASCADE)
    instagramAccount = models.ForeignKey(InstagramAccount, on_delete=models.CASCADE)