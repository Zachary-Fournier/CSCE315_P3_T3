from django.urls import path
from . import views

urlpatterns = [
    path("<int:nm>", views.test, name="test"),
    path("", views.home, name="home"),
]
