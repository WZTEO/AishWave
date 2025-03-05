from django.shortcuts import redirect
from django.urls import reverse
from allauth.account.utils import perform_login
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model
from shop.models import ReferralCode
import uuid

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter, DefaultAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get("email")
        if not email:
            return  # No email, continue the normal flow

        try:
            existing_user = User.objects.get(email=email)

            if sociallogin.is_existing:
                return  # The user already has this social account, allow login

            # Link the social account to the existing user
            sociallogin.connect(request, existing_user)

            # Log in the existing user
            perform_login(request, existing_user, email_verification="optional")

            # Redirect to the home page or any custom URL
            raise ImmediateHttpResponse(redirect("/"))

        except User.DoesNotExist:
            pass  # No existing user, continue normal sign-up process

    def send_mail(self, template_prefix, email, context):
        # Store email in session so it can be used on the reset done page
        self.request.session["password_reset_email"] = email
        super().send_mail(template_prefix, email, context)

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        # Ensure every social login user gets a referral code
        if not ReferralCode.objects.filter(user=user).exists():
            ReferralCode.objects.create(user=user, code=str(uuid.uuid4())[:10].upper())

        return user