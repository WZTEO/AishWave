# from django.contrib.admin import AdminSite
# from django.contrib import admin
# from accountAuth.models import CustomUser
# from ..models import *  # or import them individually
# from ..admin import *   # import your original admin classes

# from django.contrib.auth.admin import UserAdmin
# from django.utils.translation import gettext_lazy as _

# class FullCustomUserAdmin(UserAdmin):
#     model = CustomUser
#     list_display = ('username', 'email', 'is_staff', 'is_superuser', 'is_active')
#     list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')

#     fieldsets = (
#         (None, {'fields': ('username', 'email', 'password')}),
#         (_('Permissions'), {
#             'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
#         }),
#         (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
#         }),
#     )

#     search_fields = ('email', 'username')
#     ordering = ('username',)


# class FullPowerAdmin(AdminSite):
#     site_header = "Full Admin"
#     site_title = "Super Admin Portal"
#     index_title = "Welcome to the Real Admin Panel"

#     def has_permission(self, request):
#         return request.user.is_active and request.user.is_superuser
# full_admin_site = FullPowerAdmin(name='fulladmin')

# # Register all models just like in the original
# models_to_register = [
#     CustomUser, Order, ExchangeRate, LoginHistory, ReferralAmount, BillBoardImage,
#     Task, Investment, Transaction, Referral, WithdrawalRequest, Wallet, Discount,
#     ClashTournament, BattleRoyalePlayer, BattleRoyaleTournament, Squad, SquadPlayer,
#     SquadTournament, Product, Crypto, Trade
# ]

# admin_classes = {
#     Order: OrderAdmin,
#     ExchangeRate: ExchangeRateAdmin,
#     ReferralAmount: ReferralAmountAdmin,
#     BillBoardImage: BillBoardImages,
#     Task: TaskAdmin,
#     Investment: InvestmentAdmin,
#     Transaction: TransactionAdmin,
#     Referral: ReferralAdmin,
#     WithdrawalRequest: WithdrawalRequestAdmin,
#     Wallet: WalletAdmin,
#     Discount: DiscountAdmin,
#     ClashTournament: ClashTournamentAdmin,
#     BattleRoyalePlayer: BattleRoyalePlayerAdmin,
#     BattleRoyaleTournament: BattleRoyaleTournamentAdmin,
#     Squad: SquadAdmin,
#     SquadPlayer: SquadPlayerAdmin,
#     SquadTournament: SquadTournamentAdmin,
#     Product: ProductAdmin,
#     Crypto: CryptoAdmin,
#     Trade: TradeAdmin,
# }

# for model, admin_class in admin_classes.items():
#     full_admin_site.register(model, admin_class)

# full_admin_site.register(CustomUser, FullCustomUserAdmin)
# AishWave/shop/templatetags/admni.py
from django.contrib.admin import AdminSite
from django.contrib import admin
from accountAuth.models import CustomUser
from ..models import *
from ..admin import *  # ✅ imports all admin classes automatically
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


class FullCustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'is_staff', 'is_superuser', 'groups', 'user_permissions'
            ),
        }),
    )

    search_fields = ('email', 'username')
    ordering = ('username',)


class FullPowerAdmin(AdminSite):
    site_header = "Full Admin"
    site_title = "Super Admin Portal"
    index_title = "Welcome to the Real Admin Panel"

    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser


# ✅ create custom site
full_admin_site = FullPowerAdmin(name='fulladmin')

# ✅ Register all models using the same admin classes from shop/admin.py
admin_classes = {
    Order: OrderAdmin,
    ExchangeRate: ExchangeRateAdmin,
    ReferralAmount: ReferralAmountAdmin,
    BillBoardImage: BillBoardImages,
    Task: TaskAdmin,
    Investment: InvestmentAdmin,
    Transaction: TransactionAdmin,
    Referral: ReferralAdmin,
    WithdrawalRequest: WithdrawalRequestAdmin,  # ✅ now includes your new logic
    Wallet: WalletAdmin,
    Discount: DiscountAdmin,
    ClashTournament: ClashTournamentAdmin,
    BattleRoyalePlayer: BattleRoyalePlayerAdmin,
    BattleRoyaleTournament: BattleRoyaleTournamentAdmin,
    Squad: SquadAdmin,
    SquadPlayer: SquadPlayerAdmin,
    SquadTournament: SquadTournamentAdmin,
    Product: ProductAdmin,
    Crypto: CryptoAdmin,
    Trade: TradeAdmin,
}

for model, admin_class in admin_classes.items():
    full_admin_site.register(model, admin_class)

# ✅ Register user admin too
full_admin_site.register(CustomUser, FullCustomUserAdmin)
