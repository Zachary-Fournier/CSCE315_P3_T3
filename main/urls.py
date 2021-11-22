from django.urls import path
from . import views

urlpatterns = [
    path("<int:nm>", views.test, name="test"),
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/<str:message>", views.makePost, name="makePost"),
]

"""
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("<str:message>", views.makePost, name="makePost"),
    path("connect-accounts/", views.connectAccounts, name="connectAccounts"),
]
"""
