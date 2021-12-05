from django import forms
from django.contrib.auth.models import User
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


class ImageForm(forms.Form):
    img = forms.ImageField()
    
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]