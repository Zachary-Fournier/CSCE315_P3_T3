from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("<int:form>", views.home, name="home"),
    path("platformsLogin/", views.platformsLogin, name="platformsLogin"),
    path("makePost/", views.makePost, name="makePost"),
    path("fbtoken/<str:info>", views.getFacebookToken, name="getFacebookToken"),
    path("getTwitterToken/", views.getTwitterToken, name="getTwitterToken"),
    path("twitteraccess/", views.getTwitterAccess, name="getTwitterAccess"),
    path("instagramAccess/", views.getInstagramAccess, name="getInstagramAccess"),
]
