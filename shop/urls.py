from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
urlpatterns = [
    path('shop/', shop, name='shop'),
    path('', finance, name='finance'),
    path('profile/', profile, name='profile'),
    path('contact-form/', contact_form, name='contact-form'),
    path('stocks/', stocks, name='stocks'),
    path('referral/', referral, name='referral'),
    path('investment/', create_investment, name='create_investment'),
    path('tasks/', tasks, name='tasks'),
    path('pubg/', pubg, name='pubg'),
    path('codm/', codm, name='codm'),
    path('googleplay/', googleplay, name='googleplay'),
    path('fortnite/', fortnite, name='fortnite'),
    path('steam/', steam, name='steam'),
    path('playstation/', playstation, name='playstation'),
    path('apple/', apple, name='apple'),
    path('freefire/', freefire, name='freefire'),
    path('wallet/deposit/', initiate_deposit, name='wallet_deposit'),
    path('wallet/verify-deposit/', verify_deposit, name='verify-deposit'),
    path('test/', test_view, name='test'),
    path('withdraw/', withdraw_request, name='withdrawal_request'),
    path('add-recipient/', add_recipient, name='add_recipient'),
    path('withdraw/finalize/<str:transfer_code>/', finalize_withdrawal, name='finalize_withdrawal'),
    path('resend-otp/', resend_paystack_otp, name='resend_otp'),
    path('purchase/', purchase_product, name='purchase_product'),
    path('investment/<int:investment_id>/', investment_status, name='status_investment'),
    path('rewards/', complete_task, name='rewards')

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)