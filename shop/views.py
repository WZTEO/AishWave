import dis
from itertools import product
from locale import currency
from math import prod
from poplib import CR
from unicodedata import category
from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.utils.timezone import now
from allauth.account.forms import LoginForm
from datetime import timedelta
from django.http import JsonResponse
from .models import  (
    BattleRoyalePlayer, Wallet, Task, TaskCompletion, ReferralAmount, Transaction, BillBoardImage, 
    LoginHistory,PaystackRecipient, Order, Investment, Referral, WithdrawalRequest, Crypto,
    Discount, ExchangeRate, ReferralCode, ClashTournament, BattleRoyalePlayer, Squad, Product, Trade )
from .utils import create_paystack_recipient
from django.contrib.sessions.models import Session
from django.db.models import Sum
from decimal import Decimal
import requests
import json
# Create your views here.

def shop(request):
    discount = Discount.objects.all()
    images = BillBoardImage.objects.all()
    return render(request, 'shop/shop.html', {"discounts": discount, "images": images})

@login_required
def finance(request):
    user_wallet = None
    transactions = []
    orders = []
    investments = []

    if request.user.is_authenticated:
        user_wallet, created = Wallet.objects.get_or_create(user=request.user)
        transactions = Transaction.objects.filter(wallet=user_wallet).order_by("-created_at")
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        investments = Investment.objects.filter(user=request.user, end_date__gt=now())

    return render(request, 'shop/new_finance.html', {
        "transactions": transactions,
        "wallet": user_wallet,
        "today_date": now().date(),
        "orders": orders,
        "investments": investments
    })

@login_required
def profile(request):
    history = LoginHistory.objects.filter(user=request.user).order_by("-timestamp")
    return render(request, 'shop/profile.html', {'history': history})

@login_required
def contact_form(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        send_mail(
            subject=f"New Contact Form Submission from {name}",
            message=f"Name: {name} \nEmail: {email}\n\n Message: \n{message}", 
            from_email=settings.DEFAULT_FROM_EMAIL, #email address
            recipient_list=[settings.RECIPIENT_EMAIL], #admin email
            fail_silently=False,
        )
        messages.success(request, "Your request has been submitted")
        return redirect("finance")
    return render(request, 'shop/contact-form.html')

@login_required
def stocks(request):
    return render(request, 'shop/stocks.html')

@login_required
def referral(request):
    user = request.user
    referrals = Referral.objects.filter(referrer=user)

    # Get the referral code from the first referral
    referral_code = ReferralCode.objects.filter(user=user).first()
    referral_amount = ReferralAmount.objects.first()

    return render(request, 'shop/referral.html', {
        "total_earnings": round(Referral.get_total_earnings(user), 2),
        "total_referrals": referrals.count(),
        "referral_code": referral_code.code, 
        "referral_amount": referral_amount,
    })

@login_required
def investment(request):
    return render(request, 'shop/investment.html')

@login_required
def tasks(request):
    tasks = Task.objects.all()
    return render(request, 'shop/tasks.html', {"tasks": tasks})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    cryptos = Crypto.objects.all()
    return render(request, f'shop_update/{product.slug}.html', {'product': product, 'cryptos': cryptos})

@login_required
def initiate_deposit(request):
    if request.method == 'POST':
        amount = int(request.POST.get("amount")) * 100 #convert to peswas
        if int(request.POST.get("amount")) < 20:
            messages.error(request, "Minimum deposit amount is GHS 20", extra_tags="deposit")
            return redirect("wallet_deposit")
        
        email = request.user.email

        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "AUthorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "email": email,
            "amount": amount,
            "currency": "GHS",
            "callback_url": f"{settings.PAYSTACK_CALLBACK}/wallet/verify-deposit/"
        }
        response = requests.post(url, json=payload, headers=headers)
        print(f"Paystack response:", response.text)
        res_data = response.json()
        if res_data.get("status"):
            return redirect(res_data["data"]["authorization_url"]) #redirect to paystack
        
    return render(request, "wallet/deposit.html")
    
@login_required
def verify_deposit(request):
    reference = request.GET.get("reference")

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }
    response = requests.get(url, headers=headers)
    res_data = response.json()
    
    if res_data.get("status") and res_data["data"]["status"] == "success":
        amount = res_data["data"]["amount"] / 100 #convert to GHS
        user_wallet, created = Wallet.objects.get_or_create(user=request.user)
        user_wallet.deposit(amount)

        Transaction.objects.create(
            wallet=user_wallet,
            amount=amount,
            transaction_type="deposit",
            reference=reference,
            status="success"
        )
        #return JsonResponse({"message": "Deposit successful", "balance": user_wallet.balance})
        return redirect("finance")
    #return JsonResponse({"error": "Deposit failed!"}, status=400)
    return redirect("wallet_deposit")

@login_required
def add_recipient(request):
    if request.method == 'POST':
        account_number = request.POST["account_number"]
        provider_name = request.POST["provider"]
        user = request.user
        recipient_name=request.POST["recipient_name"]

        # Set bank codes for MoMo providers
        bank_codes = {
            "MTN": "MTN",
            "Vodafone": "VOD",
            "AirtelTigo": "ATL"
        }
        bank_code = bank_codes.get(provider_name)

        if not bank_code:
            messages.error(request, "Invalid MoMo provider selected.")
            return redirect("add_recipient")
        
        payload = {
            "type": "mobile_money",
            "name": user.get_full_name(),
            "account_number": account_number,
            "bank_code": bank_code,
            "currency": "GHS"
        }

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        url = "https://api.paystack.co/transferrecipient"
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        print(f"REsponse: {response_data}")

        if response_data.get("status"):
            recipient_code = response_data["data"]["recipient_code"]

            PaystackRecipient.objects.create(
                user=user,
                recipient_code=recipient_code,
                provider_name=provider_name,
                account_number=account_number,
                recipient_name=recipient_name
            )
            return redirect("withdrawal_request")
        else:
            messages.error(request, "Could not add recipient, try again.")
            return redirect("add_recipient")

    return render(request, "wallet/add_recipient.html")

def get_bank_codes():
    """Fetch available bank codes from Paystack API."""
    url = "https://api.paystack.co/bank"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    response = requests.get(url, headers=headers)
    banks = response.json().get("data", [])
    return banks  # List of banks with 'name' and 'code'

@login_required
def withdraw_request(request):
    if request.method == 'POST':
        amount = request.POST.get("amount")
        # recipient_code = request.POST.get("recipient_code")
        recipient_name = request.POST.get("account_name")
        account_number = request.POST.get("account_number")
        provider = request.POST.get("provider")

        if provider in ["mtn", "vodafone"] and int(amount) < 100:
            messages.error(request, "Minimum withrawal is GHS 100", extra_tags="withdrawal")
            return redirect("withdrawal_request")

        if provider == "binance" and int(amount) < 10:
            messages.error(request, "Minimum withdrawal is $10", extra_tags="withdrawal")
            return redirect("withdrawal_request")


        if WithdrawalRequest.objects.filter(user=request.user, status="pending"):
            messages.error(request, "You already have a pending withdrawal request!", extra_tags="withdrawal")
            return redirect("withdrawal_request")
        if not amount or not recipient_name or not account_number:
            messages.error(request,"This field is required", extra_tags="withdrawal")
            return redirect("withdrawal_request")
        user_wallet = Wallet.objects.get(user=request.user)
        recipient = PaystackRecipient.objects.create(
            user=request.user,
            provider_name=provider,
            recipient_name=recipient_name,
            account_number=account_number,
        )
        # if not recipient:
        #     print("You need to add a payment method first")
        #     messages.info(request, "You need to add a recipient to make withdrawals")
        #     return redirect("add_recipient")

        if Decimal(amount) > user_wallet.balance:
            print("Insufficient balance")
            messages.error(request, "Insufficient balance.", extra_tags="withdrawal")
            return redirect("withdrawal_request")
        else:
            WithdrawalRequest.objects.create(
                user=request.user,
                amount=amount,
                recipient=recipient
                )
            print("Request submitted")

            Transaction.objects.create(
                    wallet=user_wallet,
                    amount=amount,
                    transaction_type="withdrawal",
                    status="pending"
                )
            messages.success(request, "Withdrawal request submitted.", extra_tags="withdrawal")
            return redirect("finance")
        
    momo_recipients = PaystackRecipient.objects.filter(user=request.user)
    return render(request, 'wallet/withdraw.html', {"momo_recipients": momo_recipients})

@login_required
def finalize_withdrawal(request, transfer_code):
    if request.method == 'POST':
        otp = request.POST.get("otp")
        user_wallet = Wallet.objects.get(user=request.user)

        if not transfer_code or not otp:
            return JsonResponse({"error": "OTP and reference are required."})

        url = "https://api.paystack.co/transfer/finalize_transfer"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "transfer_code": transfer_code,
            "otp": otp
        }
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()

        if res_data.get("status"):
            # OTP confirmed, now deduct balance
            transaction = Transaction.objects.get(reference=transfer_code)
            if user_wallet.withdraw(transaction.amount):  # Ensure the balance is available
                transaction.status = "successful"
                transaction.save()
                #return JsonResponse({"message": "Withdrawal successful"})
                return redirect("finance")
            else:
                return JsonResponse({"error": "Insufficient balance for withdrawal"})
        else:
            return JsonResponse({"error": "Failed to finalize withdrawal. Try again"})

    return render(request, "wallet/otp.html", {"transfer_code": transfer_code})

@login_required
def resend_paystack_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body) if request.content_type == "application/json" else request.POST
            transfer_code = data.get("transfer_code")

            if not transfer_code:
                return JsonResponse({"success": False, "message": "Transfer code is required"}, status=400)

            response = request_paystack_otp(transfer_code)
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON data"}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

@login_required
def request_paystack_otp(transfer_code):
    url = "https://api.paystack.co/transfer/resend_otp"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"transfer_code": transfer_code, "reason": "resend_otp"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get("status"):
            return {"success": True, "message": response_data.get("message")}
        else:
            return {"success": False, "message": response_data.get("message", "Failed to resend OTP")}

    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Error: {str(e)}"}

def test_view(request):
    print("User:", request.user)
    print("Authenticated:", request.user.is_authenticated)
    return JsonResponse({"user": str(request.user), "authenticated": request.user.is_authenticated})

@login_required
def purchase_product(request):
    if request.method == 'POST':
        selected_item = request.POST.get('selected_item')
        player_id = request.POST.get('player_id')
        form_product = request.POST.get('product')
        if not selected_item:
            pass

    user_wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    try:
        product_name, price = selected_item.rsplit(',',1)
        price_in_usd = Decimal(price) #price is USD
        
        #discount = Discount.objects.first()
        product = get_object_or_404(Product, slug=form_product)
        discount_value = product.discount
        print(f"Product: {product_name}, Discount: {discount_value}%")
        print(f"Discount valuee: {discount_value}%")

        discount_value = discount_value / Decimal(100)
        price = max(price_in_usd - (price_in_usd * discount_value), Decimal(0))
        price_in_ghs = ExchangeRate.convert_to_ghs(price)
        print(f"{product_name} - {price_in_ghs}")
        formatted_order = f"{product.name} - {product_name}"

        if user_wallet.balance >= price_in_ghs:
            user_wallet.balance -= price_in_ghs
            user_wallet.save()
            order = Order.objects.create(
                    user=request.user,
                    player_id=player_id,
                    amount=price_in_ghs,
                    product=formatted_order,
                    status="pending",
                )
            Transaction.objects.create(
                    wallet=user_wallet,
                    amount=price_in_ghs,
                    transaction_type="purchase",
                    order=order
                )
      
        else:
            messages.error(request, "Insufficient balance", extra_tags='purchase')
            print("Insufficient balance")
            return redirect('product-detail', slug=product.slug)

    except ValueError:
        print("Invalid product selection")
        messages.error(request, "Invalid product selection")
        return redirect('shop')
    return redirect('finance')

@login_required
def trade_card(request):
    if request.method == 'POST':
        product = request.POST.get('selected_gift_card')
        currency = request.POST.get('currency')
        file = request.FILES.get('card_image')
        card_type = request.POST.get('card_type')
        amount = request.POST.get('amount')
        card_code = request.POST.get('card_code')

        # Validate: image required if physical card
        if card_type == "Physical" and not file:
            messages.error(request, "An image is required for physical cards.", extra_tags="trade")
            return redirect('trade')  # or the appropriate form page
        

        try:
            trade = Trade.objects.create(
                product=product,
                amount=amount,
                currency=currency,
                card_image=file if card_type == "Physical" else None,
                card_code=card_code,
                card_type=card_type,
            )
            messages.success(request, "Trade submitted successfully.",extra_tags="trade")
            return redirect('trade')  # or wherever you redirect on success

        except ValueError as e:
            print(f"Trade error: {e}")
            messages.error(request, "Invalid trade submission.", extra_tags="trade")
            return redirect('trade')




@login_required
def create_investment(request):
    plans = {
        "quick": {
            "name": "Quick Returns Plan",
            "min": 25,
            "max": 499,
            "daily_return": 4,
            "duration": 31
        },
        "premium": {
            "name": "Premium Returns Plan",
            "min": 699,
            "max": 999,
            "daily_return": 3,
            "duration": 61
        }
    }
    
    active_investments = Investment.objects.filter(user=request.user, end_date__gt=now())

    if request.method == 'POST':
        plan = request.POST.get("plan")
        amount = int(request.POST.get("amount") or 0)
        price_in_ghs = ExchangeRate.convert_to_ghs(amount)

        # Check if the user already has an active investment in this tier
        if Investment.objects.filter(user=request.user, plan=plan, end_date__gt=now()).exists():            
            messages.error(request, "You already have an active investment in this tier!", extra_tags="investment")
            print("You already have an active investment in this tier!")
            return redirect("create_investment")

        if plan not in plans:
            messages.error(request, "Invalid investment plan", extra_tags="investment")
            print("Invalid investment plan")
            return redirect("create_investment")

        plan_data = plans[plan]

        if not (plan_data["min"] <= amount <= plan_data["max"]):
            print("Amount must be between min and max")
            return redirect("create_investment")

        wallet = Wallet.objects.get(user=request.user)
        if not wallet.deduct(price_in_ghs): # Deduct from wallet using converted price
            print("Insufficient balance")
            messages.error(request, "Insufficient balance", extra_tags="investment")
            return redirect("create_investment")

        # Create the investment
        investment = Investment.objects.create(
            user=request.user,
            amount=amount,
            plan=plan,
            daily_return=plan_data["daily_return"],
            duration=plan_data["duration"],
            start_date=now(),
            end_date=now() + timedelta(days=plan_data["duration"])
        )

        # Log the transaction
        Transaction.objects.create(
            wallet=wallet,
            amount=price_in_ghs,
            transaction_type="investment",
            status="completed"
        )

        print("Investment successfully created")
        messages.success(request, "Investment created successfully", extra_tags="investment")
        return redirect("create_investment")

    return render(request, "shop/investment.html", {
        "plans": plans,
        "investment_list": active_investments
    })

@login_required
def claim_investment_earnings(request, investment_id):
    investment = get_object_or_404(Investment, id=investment_id, user=request.user)

    if investment.claim_earnings():
        messages.success(request, "Earnings successfully claimed!", extra_tags="investment")
    else:
        messages.error(request, "Earnings cannot be claimed yet.", extra_tags="investment")

    return redirect("create_investment")  # Redirect to the investment page

@login_required
def investment_status(request, investment_id):
    try:
        investment = Investment.objects.get(id=investment_id)
        context = {
            "investment": investment,
            "time_left": investment.time_left(),
            "earned": round(investment.calculate_earnings(), 2)
        }
        return render(request, "shop/investment_status.html", context)
    except Investment.DoesNotExist:
        return render(request, "shop/investment_status.html", {"error": "Investment not found"})

@login_required
def complete_task(request):
    print("🔍 Request Method:", request.method)
    print("📦 Request Data:", request.POST)

    if request.method == "POST":
        print("✅ Got POST request.")

        task_id = request.POST.get("task_id")
        print("🆔 Task ID:", task_id)

        if not task_id:
            messages.error(request, "Task ID is missing.")
            return redirect("tasks")

        task = get_object_or_404(Task, id=task_id)

        last_completion = TaskCompletion.objects.filter(user=request.user, task=task).order_by('-completed_at').first()

        if last_completion and (now().date() - last_completion.completed_at.date()).days < 7:
            messages.error(request, "You can only claim this task once per week.", extra_tags='task')
            print("ONly once")
            return redirect("tasks")

        if TaskCompletion.objects.filter(user=request.user, task=task).exists():
            messages.error(request, "You have already completed this task.")
            print("You have already completed this task.")
            return redirect("tasks")

        # Reward the user
        user_wallet, created = Wallet.objects.get_or_create(user=request.user)
        reward_in_ghs = ExchangeRate.convert_to_ghs(task.reward_amount)
        user_wallet.balance += reward_in_ghs
        user_wallet.save()

        # Mark task as completed
        TaskCompletion.objects.create(user=request.user, task=task)

        # Log the transaction
        Transaction.objects.create(
            wallet=user_wallet,
            amount=task.reward_amount,
            transaction_type="task_reward",
            status="completed"
        )

        messages.success(request, f"You've been rewarded ${task.reward_amount} (GHS{reward_in_ghs}) for completing the task!", extra_tags='task')
        return redirect("tasks")

    messages.error(request, "Invalid request.")
    return redirect("tasks")

from django.shortcuts import render, redirect
from allauth.account.forms import LoginForm
from allauth.account.views import LoginView
from allauth.account import app_settings
from allauth.account.utils import complete_signup, perform_login
from allauth.account.adapter import get_adapter
from django.contrib.auth import login as auth_login

# def dummy_view(request):
#     form = LoginForm(data=request.POST or None)  # ✅ always pass request

#     if request.method == 'POST' and form.is_valid():
#         user = form.user
#         perform_login(request, user, email_verification=app_settings.EMAIL_VERIFICATION)
#         return redirect('/')  # or your dashboard

#     return render(request, 'homepage/landing_page.html', {'form': form})

def dummy_view(request):
    form = LoginForm(data=request.POST or None)  # ✅ always pass request

    if request.method == 'POST' and form.is_valid():
        user = form.user
        auth_login(request, user)  # Use Django's login function
        return redirect('/')  # or your dashboard

    return render(request, 'homepage/landing_page.html', {'form': form})

@login_required
def clash(request):
    group_stages = ClashTournament.objects.filter(stage="group")
    quarter_stages = ClashTournament.objects.filter(stage="quarter")
    semi_stages = ClashTournament.objects.filter(stage="semi")
    final_stages = ClashTournament.objects.filter(stage="final")
    return render(request, 'tournament/clash.html', {
        'group_stages': group_stages,
        'quarter_stages': quarter_stages,
        'semi_stages': semi_stages,
        'final_stages': final_stages
        })

@login_required
def battle_royale(request):
    players = BattleRoyalePlayer.objects.all().order_by('-kills', '-matches_played')
    return render(request, 'tournament/battle_royale.html', {'players': players})

@login_required
def squad_challenges(request):
    squads = Squad.objects.annotate(
    total_kills=Sum('players__kills')
        ).order_by('-total_kills')

    return render(request, 'tournament/squad.html', {'squads': squads})

@login_required
def rules(request):
    return render(request, 'tournament/rules.html')


def shop_update(request):
    ecommerce_products = Product.objects.all().filter(category="ecommerce")
    esim_products = Product.objects.all().filter(category="esim")
    game_products = Product.objects.all().filter(category="games")
    giftcard_products = Product.objects.all().filter(category="gift-cards")
    product = Product.objects.filter(slug='crypto').first()
    billboard_images = BillBoardImage.objects.first()
    print(f"{product.slug}")
    return render(request, 'shop_update/products.html', {
        "ecommerce_products": ecommerce_products,
        "esim_products": esim_products,
        "game_products": game_products,
        "giftcard_products": giftcard_products,
        "product": product,
        "billboard_images": billboard_images,
    })

@login_required
def update_trade(request):
    gift_cards = {
        'Apple': 'https://cdn.simpleicons.org/apple/000000/ffffff',
        'Google Play': 'https://1000logos.net/wp-content/uploads/2021/07/Google-Play-Logo-500x281.png',
        'Amazon': 'https://1000logos.net/wp-content/uploads/2016/10/Amazon-Logo.png',
        'eBay': 'https://1000logos.net/wp-content/uploads/2018/10/Ebay-Logo-1.png',
        'PlayStation': 'https://cdn.simpleicons.org/playstation/000000/ffffff',
        'Steam': 'https://1000logos.net/wp-content/uploads/2020/08/Steam-Logo.png',
        'iTunes': 'https://1000logos.net/wp-content/uploads/2018/05/Itunes-logo.png',
        'Razer': 'https://cdn.simpleicons.org/razer/000000/ffffff',
    }
    return render(request, 'shop_update/trade.html', {'gift_cards': gift_cards})

@login_required
def update_esim(request):
    return render(request, 'shop_update/esim.html')

@login_required
def update_ecommerce(request):
    return render(request, 'shop_update/ecommerce.html')

@login_required
def update_crypto(request):
    cryptos = Crypto.objects.all()
    return render(request, "shop_update/crypto.html", {'cryptos': cryptos})

def terms(request):
    return render(request, "shop_update/terms.html")

@login_required
def orders(request):
    orders = Order.objects.all().filter(user=request.user)
    return render(request, "shop_update/orders.html", {'orders': orders})