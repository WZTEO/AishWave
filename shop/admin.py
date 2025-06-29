from django.contrib import admin
from django.core.mail import send_mail
from django.contrib import messages
from .models import (
    Order, ExchangeRate,LoginHistory, ReferralAmount, BillBoardImage, Task,Investment,
    Transaction, Referral, WithdrawalRequest, Wallet, Discount, ClashTournament,
    BattleRoyalePlayer, BattleRoyaleTournament, Squad, SquadPlayer, SquadTournament,
    Product, Crypto
    )
from django.contrib.auth.admin import UserAdmin
from accountAuth.models import CustomUser
from django.contrib.auth.models import Group
from allauth.socialaccount.models import SocialToken, SocialApp, SocialAccount
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from .forms import ClashTournamentForm
from decimal import Decimal
from adminsortable2.admin import SortableAdminMixin
from django.utils.translation import gettext_lazy as _

admin.site.unregister(Group)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email',  'is_active')
    list_filter = ('is_active', 'groups')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'groups'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'groups'),
        }),
    )

    search_fields = ('email', 'username')
    ordering = ('username',)

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
        """Approve selected withdrawals"""
        for withdrawal in queryset.filter(status="pending"):
            if withdrawal.approve():
                self.message_user(request, f"Withdrawal for {withdrawal.user} approved and deducted from wallet.")
            else:
                self.message_user(request, f"Insufficient funds for {withdrawal.user}.", level="error")

    def reject_withdrawals(self, request, queryset):
        """Reject selected withdrawals"""
        for withdrawal in queryset.filter(status="pending"):
            withdrawal.reject()
            self.message_user(request, f"Withdrawal for {withdrawal.user} has been rejected.")

    approve_withdrawals.short_description = "Approve selected withdrawals"
    reject_withdrawals.short_description = "Reject selected withdrawals"

@admin.register(ClashTournament)
class ClashTournamentAdmin(admin.ModelAdmin):
    form = ClashTournamentForm
    list_display = ('player1', 'player2', 'stage', 'date', 'formatted_time')
    list_filter = ('stage',)
    search_fields = ('player1', 'player2')
    ordering = ('date', 'time')

    def formatted_time(self, obj):
        return obj.get_time_display()
    formatted_time.short_description = 'Time'

@admin.register(BattleRoyalePlayer)
class BattleRoyalePlayerAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'country', 'kills', 'matches_played', 'match')
    list_filter = ('country', 'match')
    search_fields = ('player_name',)
    ordering = ('-kills',)

@admin.register(BattleRoyaleTournament)
class BattleRoyaleTournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'player_count')
    search_fields = ('name',)
    ordering = ('-created_at',)

    def player_count(self, obj):
        return obj.players.count()
    player_count.short_description = 'Players'

# Inline for players in a squad
class SquadPlayerInline(admin.TabularInline):
    model = Squad.players.through  # ManyToMany intermediary
    extra = 1
    verbose_name = "Squad Player"
    verbose_name_plural = "Squad Players"

# Admin for Squad
@admin.register(Squad)
class SquadAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'player_count', 'total_kills')
    list_filter = ('tournament',)
    search_fields = ('name',)
    inlines = [SquadPlayerInline]
    exclude = ('players',)  # Use inline instead of M2M selector

    def player_count(self, obj):
        return obj.players.count()
    player_count.short_description = 'Player Count'

    def total_kills(self, obj):
        return sum(player.kills for player in obj.players.all())
    total_kills.short_description = 'Total Kills'


# Admin for SquadPlayer
@admin.register(SquadPlayer)
class SquadPlayerAdmin(admin.ModelAdmin):
    list_display = ('player', 'kills')
    search_fields = ('player',)


# Inline for squads in a tournament
class SquadInline(admin.StackedInline):
    model = Squad
    extra = 1


# Admin for SquadTournament
@admin.register(SquadTournament)
class SquadTournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    inlines = [SquadInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')   # Show these columns in list view
    list_filter = ('category',)                          # Filter sidebar by category
    search_fields = ['name']              # Enable search by name and description
    ordering = ('name',)           

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user__username", "balance")
    search_fields = ["user__username"]

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("pubg", "codm", "freefire", "fortnite", "apple", "google", "steam", "playstation")

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_diplay = ("user", "device_info", "device_type")

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['currency', 'rate_to_ghs']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'platform', 'reward_amount']

@admin.register(Crypto)
class CryptoAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol']

from django.contrib import admin
from .models import Trade

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'product', 'amount', 'currency', 'card_type', 'card_code', 'card_image', 'created_at'
    )
    list_filter = ('card_type', 'currency')
    search_fields = ('product', 'card_code')
    readonly_fields = ('card_image_preview', 'created_at')

    def card_image_preview(self, obj):
        if obj.card_image:
            return f'<img src="{obj.card_image.url}" width="100" height="auto" style="border:1px solid #ccc;" />'
        return "No image"
    card_image_preview.allow_tags = True
    card_image_preview.short_description = "Card Image"
