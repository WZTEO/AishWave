from django.urls import path
from .views import CustomPasswordResetDoneView

urlpatterns = [
    path("accounts/password/reset/done/", CustomPasswordResetDoneView.as_view(), name="account_reset_password_done"),
]