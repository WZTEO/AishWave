from django.urls import path
from django.shortcuts import redirect
from .views import CustomPasswordResetDoneView

urlpatterns = [
    path("accounts/password/reset/done/", CustomPasswordResetDoneView.as_view(), name="account_reset_password_done"),
    path(
        'accounts/social/login/error/', 
        lambda request: redirect('account_login'), 
        name='socialaccount_login_error'
    ),
]