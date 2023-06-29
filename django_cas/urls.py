from django.urls import path

from . import views

app_name = "django_cas"

urlpatterns = [
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
]
