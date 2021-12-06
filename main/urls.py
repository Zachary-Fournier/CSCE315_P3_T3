from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("<int:form>", views.home, name="home"),
    path("platformsLogin/", views.platformsLogin, name="platformsLogin"),
    path("makePost/", views.makePost, name="makePost"),
    path("fbandigaccess/", views.getFbandIGAccess, name="getFbandIGAccess"),
    path("getTwitterToken/", views.getTwitterToken, name="getTwitterToken"),
    path("twitteraccess/", views.getTwitterAccess, name="getTwitterAccess"),
    path("getPhoto/", views.getPhoto, name="getPhoto"),
]
