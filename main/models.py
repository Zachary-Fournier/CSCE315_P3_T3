from django.db import models
from cryptography.fernet import Fernet

# Create your models here.

class SocialMediaAccount(models.Model):
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    token = models.CharField(max_length=200)
    fernet = Fernet(Fernet.generate_key())

    def setPassword(self, __password):
        self.password = self.fernet.encrypt(__password.encode())
        return

    def setToken(self, __token):
        self.token = self.fernet.encrypt(__token.encode())
        return

    def getPassword(self):
        return self.fernet.decrypt(self.password).decode()

    def getToken(self):
        return self.fernet.decrypt(self.token).decode()

class BaszlAccount(models.Model):
    baszlUser = models.CharField(max_length=200)
    baszlPass = models.CharField(max_length=200)
    twitterAccount = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, related_name="twitter")
    facebookAccount = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, related_name="facebook")
    instagramAccount = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, related_name="instagram")