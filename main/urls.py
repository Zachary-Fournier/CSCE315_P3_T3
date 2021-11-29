from django.urls import path
from . import views

urlpatterns = [
    path("<int:nm>", views.test, name="test"),
    path("", views.home, name="home"),
    path("platformsLogin/", views.platformsLogin, name="platformsLogin"),
    path("makePost/", views.makePost, name="makePost"),
]
