from django import forms
from allauth.account.forms import SignupForm
from shop.models import Referral, ReferralCode, ExchangeRate, Wallet
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
import uuid


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name', widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, label='Last Name', widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    referral_code = forms.CharField(
        max_length=10, 
        required=False, 
        label="Referral Code", 
        widget=forms.TextInput(attrs={'placeholder': 'Referral Code (optional)'}))



    def save(self, request):
        user = super().save(request)  # Save user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        referral_code_input = self.cleaned_data.get('referral_code')  # Get referral code

        # Check if the referral code exists
        if referral_code_input:
            try:
                referrer_code = ReferralCode.objects.get(code=referral_code_input)
                referrer = referrer_code.user

                # Prevent self-referral
                if referrer != user:
                    Referral.objects.create(referrer=referrer, referred_user=user, earned_from_signup=0.4)
                    referrer_wallet, created = Wallet.objects.get_or_create(user=referrer)
                    referrer_wallet.balance += Decimal(ExchangeRate.convert_to_ghs(Decimal('0.4')))
                    referrer_wallet.save()
            except ReferralCode.DoesNotExist:
                print(f"Referral code {referral_code_input} does not exist.")  # Debugging output

        # Ensure every user gets a referral code
        ReferralCode.objects.create(user=user)

        user.save()
        return user