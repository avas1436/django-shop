# core/apps/accounts/urls.py

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("account/", views.ContactView.as_view(), name="account"),
]
