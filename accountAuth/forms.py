from django import forms
from allauth.account.forms import SignupForm, LoginForm
from .models import CustomUser
from shop.models import Referral, ReferralCode

from django.contrib.auth import login as auth_login


class CustomLoginForm(LoginForm):
    def login(self, request, redirect_url=None):
        # Call the original login() to handle everything properly
        return super().login(request, redirect_url=redirect_url)

class CustomSignupForm(SignupForm):
    referral_code = forms.CharField(
        max_length=10,
        required=False,
        label="Referral Code",
        widget=forms.TextInput(attrs={'placeholder': 'Referral Code (optional)'})
    )

    def save(self, request):
        user = super().save(request)

        referral_code_input = self.cleaned_data.get('referral_code')

        if referral_code_input:
            try:
                referrer_code = ReferralCode.objects.get(code=referral_code_input)
                referrer = referrer_code.user

                if referrer != user:
                    Referral.objects.create(
                        referrer=referrer,
                        referred_user=user
                    )
            except ReferralCode.DoesNotExist:
                print(f"Referral code '{referral_code_input}' is invalid.")

        ReferralCode.objects.get_or_create(user=user)

        return user