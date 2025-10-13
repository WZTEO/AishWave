import logging
logger = logging.getLogger(__name__)

from django.contrib import admin
from django.core.mail import send_mail
from django.contrib import messages
from .models import (
    DataPurchase, Order, ExchangeRate,LoginHistory, ReferralAmount, BillBoardImage, Task,Investment,
    Transaction, Referral, WithdrawalRequest, Wallet, Discount, ClashTournament,
    BattleRoyalePlayer, BattleRoyaleTournament, Squad, SquadPlayer, SquadTournament,
    Product, Crypto, ProductTier
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

logger.info("shop/admin.py - Starting admin configuration")

admin.site.unregister(Group)
logger.info("shop/admin.py - Unregistered Group model from admin")

class StaffSafeAdmin(admin.ModelAdmin):
    """
    Base admin class that hides objects related to superusers
    for non-superuser staff users.
    """
    def get_queryset(self, request):
        logger.info(f"shop/admin.py - StaffSafeAdmin.get_queryset() called for user {request.user.username}")
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info("shop/admin.py - User is superuser, returning all objects")
            return qs
        try:
            logger.info("shop/admin.py - User is staff, excluding superuser-related objects")
            return qs.exclude(user__is_superuser=True)
        except Exception as e:
            logger.warning(f"shop/admin.py - Exception in get_queryset: {e}, returning fallback queryset")
            return qs  # Fallback if model has no `user` FK


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

    def get_queryset(self, request):
        logger.info(f"shop/admin.py - CustomUserAdmin.get_queryset() called for user {request.user.username}")
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info("shop/admin.py - Superuser accessing CustomUserAdmin, returning all users")
            return qs  # superuser sees all
        logger.info("shop/admin.py - Staff user accessing CustomUserAdmin, excluding superusers")
        return qs.exclude(is_superuser=True)

    search_fields = ('email', 'username')
    ordering = ('username',)

logger.info("shop/admin.py - Unregistering social account models if registered")
for model in [SocialToken, SocialApp, SocialAccount]:
    if admin.site.is_registered(model):
        admin.site.unregister(model)
        logger.info(f"shop/admin.py - Unregistered {model.__name__}")

# Custom SocialAccount admin
class SocialAccountAdmin(StaffSafeAdmin):
    list_display = ('user', 'provider', 'uid')
    list_filter = ('provider',)
    search_fields = ('user__username', 'user__email', 'uid')

    def get_queryset(self, request):
        logger.info(f"shop/admin.py - SocialAccountAdmin.get_queryset() called for user {request.user.username}")
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            logger.info("shop/admin.py - Superuser accessing SocialAccountAdmin, returning all social accounts")
            return qs  # superuser sees all
        logger.info("shop/admin.py - Staff user accessing SocialAccountAdmin, excluding superuser social accounts")
        return qs.exclude(is_superuser=True)



@admin.register(BillBoardImage)
class BillBoardImages(admin.ModelAdmin):
    list_display = ["image1", "image2", "image3"]
    logger.info("shop/admin.py - Registered BillBoardImages admin")

@admin.register(ReferralAmount)
class ReferralAmountAdmin(admin.ModelAdmin):
    list_display= ["purchase_reward", "signup_reward"]
    logger.info("shop/admin.py - Registered ReferralAmountAdmin admin")

@admin.register(Order)
class OrderAdmin(StaffSafeAdmin):
    list_display = ("user", "player_id","product", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "product__name")  # Ensure user is a ForeignKey
    actions = ["approve_orders", "cancel_orders"]

    @admin.action(description="Approve selected orders")
    def approve_orders(self, request, queryset):
        logger.info(f"shop/admin.py - OrderAdmin.approve_orders() called for {queryset.count()} orders")
        count = 0
        for order in queryset:
            logger.info(f"shop/admin.py - Processing order {order.id} for approval")
            if order.status == "canceled":  # Prevent duplicate refunds
                logger.info(f"shop/admin.py - Order {order.id} was canceled, deducting amount from wallet")
                user_wallet, created = Wallet.objects.get_or_create(user=order.user)
                user_wallet.balance -= order.amount
                user_wallet.save()
                logger.info(f"shop/admin.py - Wallet updated for user {order.user.username}")

            order.status = "approved"
            order.save()
            logger.info(f"shop/admin.py - Order {order.id} status updated to approved")

            # Update all related transactions (if any)
            transactions_updated = order.transaction.all().update(status="completed")
            logger.info(f"shop/admin.py - Updated {transactions_updated} transactions for order {order.id}")

            # Find the correct referrer and reward them
            referral = Referral.objects.filter(referred_user=order.user).first()
            referral_amount = ReferralAmount.objects.first()
            logger.info(f"shop/admin.py - Found referral: {referral}, referral amount: {referral_amount}")
            
            if referral and referral.referrer and order.amount >= ExchangeRate.convert_to_ghs(10):  # Ensure referrer exists
                logger.info(f"shop/admin.py - Applying referral reward for order {order.id}")
                referral.earned_from_purchases += referral_amount.purchase_reward
                referral.received_reward = True  # Track that the reward was given
                referral.save()
                logger.info(f"shop/admin.py - Referral earnings updated")

                referrer_wallet, created = Wallet.objects.get_or_create(user=referral.referrer)
                reward_amount = Decimal(str(ExchangeRate.convert_to_ghs(referral_amount.purchase_reward)))
                referrer_wallet.balance += reward_amount
                referrer_wallet.save()
                logger.info(f"shop/admin.py - Referrer wallet updated with reward: {reward_amount}")

            count += 1
            logger.info(f"shop/admin.py - Completed processing order {order.id}")

        self.message_user(request, f"{count} orders approved, transactions marked as completed, and referral rewards updated.", messages.SUCCESS)
        logger.info(f"shop/admin.py - approve_orders completed for {count} orders")

    @admin.action(description="Cancel selected orders")
    def cancel_orders(self, request, queryset):
        logger.info(f"shop/admin.py - OrderAdmin.cancel_orders() called for {queryset.count()} orders")
        count = 0
        for order in queryset:
            logger.info(f"shop/admin.py - Processing order {order.id} for cancellation")
            if order.status != "canceled":  # Prevent duplicate refunds
                user_wallet, created = Wallet.objects.get_or_create(user=order.user)
                user_wallet.balance += order.amount
                user_wallet.save()
                logger.info(f"shop/admin.py - Wallet refunded for user {order.user.username}")

                # Mark transaction as canceled
                transactions_updated = order.transaction.all().update(status="canceled")
                order.status = "canceled"
                order.save()
                logger.info(f"shop/admin.py - Order {order.id} status updated to canceled, {transactions_updated} transactions updated")

                # Find the referrer and remove reward *only if it was previously given*
                referral = Referral.objects.filter(referred_user=order.user).first()
                if referral and referral.referrer and referral.received_reward:
                    logger.info(f"shop/admin.py - Removing referral reward for canceled order {order.id}")
                    referral_amount = ReferralAmount.objects.first()  
                    referral.earned_from_purchases -= referral_amount.purchase_reward
                    referral.received_reward = False  # Reset reward status
                    referral.save()
                    logger.info(f"shop/admin.py - Referral earnings adjusted")

                    referrer_wallet, created = Wallet.objects.get_or_create(user=referral.referrer)
                    deduction_amount = Decimal(str(ExchangeRate.convert_to_ghs(referral_amount.purchase_reward)))
                    referrer_wallet.balance -= deduction_amount
                    referrer_wallet.save()
                    logger.info(f"shop/admin.py - Referrer wallet adjusted by: -{deduction_amount}")

                count += 1
                logger.info(f"shop/admin.py - Completed processing order {order.id} cancellation")
            else:
                logger.info(f"shop/admin.py - Order {order.id} already canceled, skipping")

        self.message_user(request, f"{count} orders refunded and marked as Canceled.", messages.WARNING)
        logger.info(f"shop/admin.py - cancel_orders completed for {count} orders")

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "amount", "end_date", "daily_return")
    list_filter = ("plan", "end_date")
    logger.info("shop/admin.py - Registered InvestmentAdmin")

@admin.register(Transaction)
class TransactionAdmin(StaffSafeAdmin):
    list_display = ("transaction_type", "amount", "reference", "status", "created_at")
    list_filter = ("transaction_type", "status", "created_at")
    logger.info("shop/admin.py - Registered TransactionAdmin")

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referred_user", "earned_from_signup", "earned_from_purchases")
    list_filter = ("referrer", "earned_from_signup", "earned_from_purchases")
    logger.info("shop/admin.py - Registered ReferralAdmin")

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(StaffSafeAdmin):
    list_display = ("user", "amount", "recipient", "status", "created_at", "processed_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "recipient__name", "amount")
    actions = ["approve_withdrawals", "reject_withdrawals"]

    def approve_withdrawals(self, request, queryset):
        """Approve selected withdrawals"""
        logger.info(f"shop/admin.py - WithdrawalRequestAdmin.approve_withdrawals() called for {queryset.count()} withdrawals")
        for withdrawal in queryset.filter(status="pending"):
            logger.info(f"shop/admin.py - Processing withdrawal approval for user {withdrawal.user.username}, amount: {withdrawal.amount}")
            if withdrawal.approve():
                self.message_user(request, f"Withdrawal for {withdrawal.user} approved and deducted from wallet.")
                logger.info(f"shop/admin.py - Withdrawal {withdrawal.id} approved successfully")
            else:
                self.message_user(request, f"Insufficient funds for {withdrawal.user}.", level="error")
                logger.warning(f"shop/admin.py - Withdrawal {withdrawal.id} failed - insufficient funds")

    def reject_withdrawals(self, request, queryset):
        """Reject selected withdrawals"""
        logger.info(f"shop/admin.py - WithdrawalRequestAdmin.reject_withdrawals() called for {queryset.count()} withdrawals")
        for withdrawal in queryset.filter(status="pending"):
            logger.info(f"shop/admin.py - Processing withdrawal rejection for user {withdrawal.user.username}, amount: {withdrawal.amount}")
            withdrawal.reject()
            self.message_user(request, f"Withdrawal for {withdrawal.user} has been rejected.")
            logger.info(f"shop/admin.py - Withdrawal {withdrawal.id} rejected")

    approve_withdrawals.short_description = "Approve selected withdrawals"
    reject_withdrawals.short_description = "Reject selected withdrawals"
    logger.info("shop/admin.py - Registered WithdrawalRequestAdmin")

@admin.register(ClashTournament)
class ClashTournamentAdmin(admin.ModelAdmin):
    form = ClashTournamentForm
    list_display = ('player1', 'player2', 'stage', 'date', 'formatted_time')
    list_filter = ('stage',)
    search_fields = ('player1', 'player2')
    ordering = ('date', 'time')

    def formatted_time(self, obj):
        logger.info(f"shop/admin.py - ClashTournamentAdmin.formatted_time() called for tournament {obj.id}")
        result = obj.get_time_display()
        logger.info(f"shop/admin.py - Formatted time for tournament {obj.id}: {result}")
        return result
    formatted_time.short_description = 'Time'
    logger.info("shop/admin.py - Registered ClashTournamentAdmin")

@admin.register(BattleRoyalePlayer)
class BattleRoyalePlayerAdmin(admin.ModelAdmin):
    list_display = ('player_name', 'country', 'kills', 'matches_played', 'match')
    list_filter = ('country', 'match')
    search_fields = ('player_name',)
    ordering = ('-kills',)
    logger.info("shop/admin.py - Registered BattleRoyalePlayerAdmin")

@admin.register(BattleRoyaleTournament)
class BattleRoyaleTournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'player_count')
    search_fields = ('name',)
    ordering = ('-created_at',)

    def player_count(self, obj):
        logger.info(f"shop/admin.py - BattleRoyaleTournamentAdmin.player_count() called for tournament {obj.id}")
        count = obj.players.count()
        logger.info(f"shop/admin.py - Tournament {obj.id} has {count} players")
        return count
    player_count.short_description = 'Players'
    logger.info("shop/admin.py - Registered BattleRoyaleTournamentAdmin")

# Inline for players in a squad
class SquadPlayerInline(admin.TabularInline):
    model = Squad.players.through  # ManyToMany intermediary
    extra = 1
    verbose_name = "Squad Player"
    verbose_name_plural = "Squad Players"
    logger.info("shop/admin.py - Defined SquadPlayerInline")

# Admin for Squad
@admin.register(Squad)
class SquadAdmin(admin.ModelAdmin):
    list_display = ('name', 'tournament', 'player_count', 'total_kills')
    list_filter = ('tournament',)
    search_fields = ('name',)
    inlines = [SquadPlayerInline]
    exclude = ('players',)  # Use inline instead of M2M selector

    def player_count(self, obj):
        logger.info(f"shop/admin.py - SquadAdmin.player_count() called for squad {obj.id}")
        count = obj.players.count()
        logger.info(f"shop/admin.py - Squad {obj.id} has {count} players")
        return count
    player_count.short_description = 'Player Count'

    def total_kills(self, obj):
        logger.info(f"shop/admin.py - SquadAdmin.total_kills() called for squad {obj.id}")
        kills = sum(player.kills for player in obj.players.all())
        logger.info(f"shop/admin.py - Squad {obj.id} total kills: {kills}")
        return kills
    total_kills.short_description = 'Total Kills'
    logger.info("shop/admin.py - Registered SquadAdmin")


# Admin for SquadPlayer
@admin.register(SquadPlayer)
class SquadPlayerAdmin(admin.ModelAdmin):
    list_display = ('player', 'kills')
    search_fields = ('player',)
    logger.info("shop/admin.py - Registered SquadPlayerAdmin")


# Inline for squads in a tournament
class SquadInline(admin.StackedInline):
    model = Squad
    extra = 1
    logger.info("shop/admin.py - Defined SquadInline")

# Admin for SquadTournament
@admin.register(SquadTournament)
class SquadTournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    inlines = [SquadInline]
    logger.info("shop/admin.py - Registered SquadTournamentAdmin")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')   # Show these columns in list view
    list_filter = ('category',)                          # Filter sidebar by category
    search_fields = ['name']              # Enable search by name and description
    ordering = ('name',)
    logger.info("shop/admin.py - Registered ProductAdmin")

@admin.register(ProductTier)
class ProductTierAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'price', 'price_currency')
    logger.info("shop/admin.py - Registered ProductTierAdmin")

@admin.register(Wallet)
class WalletAdmin(StaffSafeAdmin):
    list_display = ("user__username", "balance")
    search_fields = ["user__username"]
    logger.info("shop/admin.py - Registered WalletAdmin")

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("pubg", "codm", "freefire", "fortnite", "apple", "google", "steam", "playstation")
    logger.info("shop/admin.py - Registered DiscountAdmin")

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['currency', 'rate_to_ghs']
    logger.info("shop/admin.py - Registered ExchangeRateAdmin")

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'platform', 'reward_amount']
    logger.info("shop/admin.py - Registered TaskAdmin")

@admin.register(Crypto)
class CryptoAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol']
    logger.info("shop/admin.py - Registered CryptoAdmin")

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
        logger.info(f"shop/admin.py - TradeAdmin.card_image_preview() called for trade {obj.id}")
        if obj.card_image:
            result = f'<img src="{obj.card_image.url}" width="100" height="auto" style="border:1px solid #ccc;" />'
            logger.info(f"shop/admin.py - Trade {obj.id} has card image")
            return result
        logger.info(f"shop/admin.py - Trade {obj.id} has no card image")
        return "No image"
    card_image_preview.allow_tags = True
    card_image_preview.short_description = "Card Image"
    logger.info("shop/admin.py - Registered TradeAdmin")






















































































@admin.register(DataPurchase)
class DataPurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "provider",
        "bundle_size",
        "price_ghs",
        "beneficiary_number",
        "status",
        "created_at",
        "processed_at",
    )
    list_filter = ("provider", "status", "created_at")
    search_fields = ("user__username", "beneficiary_number", "reference")
    actions = ["approve_purchases", "reject_purchases"]

    @admin.action(description="✅ Approve selected data purchases")
    def approve_purchases(self, request, queryset):
        logger.info(f"shop/admin.py - Approving {queryset.count()} DataPurchases")
        count = 0
        for purchase in queryset.filter(status="pending"):
            result = purchase.approve()
            if result:
                count += 1
                logger.info(f"shop/admin.py - DataPurchase {purchase.id} approved successfully")
            else:
                logger.warning(f"shop/admin.py - DataPurchase {purchase.id} failed to approve")
        self.message_user(
            request,
            f"{count} data purchases approved successfully.",
            level=messages.SUCCESS,
        )

    @admin.action(description="❌ Reject selected data purchases")
    def reject_purchases(self, request, queryset):
        logger.info(f"shop/admin.py - Rejecting {queryset.count()} DataPurchases")
        count = 0
        for purchase in queryset.filter(status="pending"):
            purchase.reject("Rejected manually by admin.")
            count += 1
        self.message_user(
            request,
            f"{count} data purchases rejected.",
            level=messages.WARNING,
        )

    logger.info("shop/admin.py - Registered DataPurchaseAdmin")


logger.info("shop/admin.py - All admin models registered successfully")