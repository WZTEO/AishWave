from django.contrib import admin
from django.core.mail import send_mail
from django.contrib import messages
from .models import Order, ExchangeRate,LoginHistory, ReferralAmount, BillBoardImage, Task,Investment, Transaction, Referral, WithdrawalRequest, Wallet, Discount
from django.contrib.auth.models import Group
from allauth.socialaccount.models import SocialToken, SocialApp, SocialAccount
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from decimal import Decimal

admin.site.unregister(Group)

# Unregister social-related models
for model in [SocialToken, SocialApp, SocialAccount]:
    if admin.site.is_registered(model):
        admin.site.unregister(model)

@admin.register(BillBoardImage)
class BillBoardImages(admin.ModelAdmin):
    list_display = ["image_url"]

@admin.register(ReferralAmount)
class ReferralAmountAdmin(admin.ModelAdmin):
    list_display= ["purchase_reward", "signup_reward"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "player_id","product", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "product__name")  # Ensure user is a ForeignKey
    actions = ["approve_orders", "cancel_orders"]

    @admin.action(description="Approve selected orders")
    def approve_orders(self, request, queryset):
        count = 0
        for order in queryset:
            if order.status == "canceled":  # Prevent duplicate refunds
                user_wallet, created = Wallet.objects.get_or_create(user=order.user)
                user_wallet.balance -= order.amount
                user_wallet.save()

            order.status = "approved"
            order.save()

            # Update all related transactions (if any)
            order.transaction.all().update(status="completed")

            # Find the correct referrer and reward them
            referral = Referral.objects.filter(referred_user=order.user).first()
            referral_amount = ReferralAmount.objects.first()
            if referral and referral.referrer and order.amount >= ExchangeRate.convert_to_ghs(10):  # Ensure referrer exists
                referral.earned_from_purchases += referral_amount.purchase_reward
                referral.received_reward = True  # Track that the reward was given
                referral.save()

                referrer_wallet, created = Wallet.objects.get_or_create(user=referral.referrer)
                referrer_wallet.balance += Decimal(str(ExchangeRate.convert_to_ghs(referral_amount.purchase_reward)))
                referrer_wallet.save()


            count += 1

        self.message_user(request, f"{count} orders approved, transactions marked as completed, and referral rewards updated.", messages.SUCCESS)  
    
    @admin.action(description="Cancel selected orders")
    def cancel_orders(self, request, queryset):
        count = 0
        for order in queryset:
            if order.status != "canceled":  # Prevent duplicate refunds
                user_wallet, created = Wallet.objects.get_or_create(user=order.user)
                user_wallet.balance += order.amount
                user_wallet.save()

                # Mark transaction as canceled
                order.transaction.all().update(status="canceled")
                order.status = "canceled"
                order.save()

                # Find the referrer and remove reward *only if it was previously given*
                referral = Referral.objects.filter(referred_user=order.user).first()
                if referral and referral.referrer and referral.received_reward:
                    referral_amount = ReferralAmount.objects.first()  
                    referral.earned_from_purchases -= referral_amount.purchase_reward
                    referral.received_reward = False  # Reset reward status
                    referral.save()

                    referrer_wallet, created = Wallet.objects.get_or_create(user=referral.referrer)
                    referrer_wallet.balance -= Decimal(str(ExchangeRate.convert_to_ghs(referral_amount.purchase_reward)))
                    referrer_wallet.save()

                count += 1

        self.message_user(request, f"{count} orders refunded and marked as Canceled.", messages.WARNING)                

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "amount", "end_date", "daily_return")
    list_filter = ("plan", "end_date")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_type", "amount", "reference", "status", "created_at")
    list_filter = ("transaction_type", "status", "created_at")

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referred_user", "earned_from_signup", "earned_from_purchases")
    list_filter = ("referrer", "earned_from_signup", "earned_from_purchases")

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "recipient", "status", "created_at", "processed_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "recipient__name", "amount")
    actions = ["approve_withdrawals", "reject_withdrawals"]

    def approve_withdrawals(self, request, queryset):
        for withdrawal in queryset.filter(status="pending"):
            if withdrawal.approve():
                self.message_user(request, f"Withdrawal for {withdrawal.user} approved.")
            else:
                self.message_user(request, f"Insufficient funds for {withdrawal.user}.", level="error")
    
    def reject_withdrawals(self, request, queryset):
        queryset.filter(status="pending").update(status="rejected", processed_at=timezone.now())
        self.message_user(request, "Selected withdrawals have been rejected.")

    approve_withdrawals.short_description = "Approve selected withdrawals"
    reject_withdrawals.short_description = "Reject selected withdrawals"

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user__username", "balance")

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("pubg", "codm", "free_fire", "fortnite", "apple", "google", "steam", "play_station")

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_diplay = ("user", "device_info", "device_type")

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['currency', 'rate_to_ghs']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'platform', 'reward_amount']