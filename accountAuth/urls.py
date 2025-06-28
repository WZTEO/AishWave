from django.urls import path
from .views import login_view, signup_view, logout

urlpatterns = [
    path("login/", login_view, name="custom-login"),
    path("signup/", signup_view, name="custom-signup"),
    path("logout/", logout, name="logout")
]