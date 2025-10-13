import logging
logger = logging.getLogger(__name__)

from encodings.punycode import T
from unicodedata import category
from django.db import models
from django.db.models import Sum, F
from decimal import Decimal
from django.utils.timezone import now
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
import uuid
# Create your models here.

User = get_user_model()

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username}'s Wallet"

    def deposit(self, amount):
        """Credit user's wallet"""
        logger.info(f"models.py - Wallet.deposit() called for user {self.user.username}, amount: {amount}")
        self.balance += Decimal(str(amount))
        self.save()
        logger.info(f"models.py - Wallet.deposit() completed. New balance: {self.balance}")

    def withdraw(self, amount):
        logger.info(f"models.py - Wallet.withdraw() called for user {self.user.username}, amount: {amount}")
        amount = Decimal(str(amount))
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            logger.info(f"models.py - Wallet.withdraw() successful. New balance: {self.balance}")
            return True
        logger.warning(f"models.py - Wallet.withdraw() failed - insufficient balance. Current: {self.balance}, Requested: {amount}")
        return False # Insufficient balance
    
    def deduct(self, amount):
        logger.info(f"models.py - Wallet.deduct() called for user {self.user.username}, amount: {amount}")
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            logger.info(f"models.py - Wallet.deduct() successful. New balance: {self.balance}")
            return True
        logger.warning(f"models.py - Wallet.deduct() failed - insufficient balance")
        return False

    def add(self, amount):
        logger.info(f"models.py - Wallet.add() called for user {self.user.username}, amount: {amount}")
        self.balance += amount
        self.save()
        logger.info(f"models.py - Wallet.add() completed. New balance: {self.balance}")

    def update_balance(self):
        """Calculate earnings for all active investments and update the wallet balance"""
        logger.info(f"models.py - Wallet.update_balance() called for user {self.user.username}")
        investments = self.user.investments.filter(status="active")
        logger.info(f"models.py - Found {investments.count()} active investments")
        total_earnings = sum(investments.calculate_earnings() for investment in investments)
        logger.info(f"models.py - Total earnings calculated: {total_earnings}")
        if total_earnings > 0:
            self.balance += total_earnings
            self.save()
            logger.info(f"models.py - Balance updated with earnings. New balance: {self.balance}")
        for investment in investments:
            investment.check_completion
        logger.info(f"models.py - Wallet.update_balance() completed")

class PaystackRecipient(models.Model):
    PAYMENT_TYPES= [
        ('mobile_money', 'Mobile Money'),
        ('bank', 'Bank Transfer')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipient_name = models.CharField(max_length=100, null=True, blank=True)
    provider_name = models.CharField(max_length=100) #Bank or momo provider
    account_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.recipient_name} - {self.provider_name}({self.account_number})"

class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected")
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipient = models.ForeignKey(PaystackRecipient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def approve(self):
        """Deduct balance and mark as approved safely."""
        logger.info(f"models.py - WithdrawalRequest.approve() called for withdrawal {self.id}, user: {self.user.username}, amount: {self.amount}")
        
        if self.status != "pending":
            logger.warning(f"models.py - Withdrawal {self.id} already processed — status={self.status}, cannot approve")
            print(f"[WARN] Withdrawal {self.id} already processed — status={self.status}")
            return False

        try:
            logger.info(f"models.py - Attempting to get wallet for user {self.user.username}")
            wallet = Wallet.objects.get(user=self.user)
            logger.info(f"models.py - Wallet found for user {self.user.username}, current balance: {wallet.balance}")
        except Wallet.DoesNotExist:
            logger.error(f"models.py - No wallet found for user {self.user.username} (ID: {self.user.id})")
            print(f"[ERROR] No wallet found for user {self.user}")
            return False
        except Exception as e:
            logger.error(f"models.py - Unexpected error getting wallet for user {self.user.username}: {str(e)}")
            print(f"[ERROR] Unexpected error getting wallet: {str(e)}")
            return False

        # Attempt to find matching transaction
        logger.info(f"models.py - Searching for matching transaction for withdrawal {self.id}")
        transaction = Transaction.objects.filter(
            wallet=wallet,
            amount=self.amount,
            transaction_type="withdrawal",
        ).first()

        if transaction:
            logger.info(f"models.py - Found matching transaction: {transaction.reference}, status: {transaction.status}")
        else:
            logger.warning(f"models.py - No matching transaction found for withdrawal {self.id}")

        # Check wallet balance
        logger.info(f"models.py - Checking wallet balance for withdrawal {self.id}")
        logger.info(f"models.py - Wallet balance: {wallet.balance}, Withdrawal amount: {self.amount}")
        
        if wallet.balance < self.amount:
            logger.error(f"models.py - Insufficient funds for user {self.user.username}. Wallet={wallet.balance}, Amount={self.amount}, Difference={wallet.balance - self.amount}")
            print(f"[ERROR] Insufficient funds for {self.user.username}. "
                f"Wallet={wallet.balance}, Amount={self.amount}")
            return False
        else:
            logger.info(f"models.py - Sufficient funds available for withdrawal {self.id}")

        # Deduct funds
        logger.info(f"models.py - Deducting {self.amount} from wallet for user {self.user.username}")
        old_balance = wallet.balance
        wallet.balance -= self.amount
        wallet.save(update_fields=["balance"])
        logger.info(f"models.py - Wallet updated for {self.user.username}: old balance={old_balance}, new balance={wallet.balance}")
        print(f"[INFO] Wallet updated for {self.user.username}: new balance={wallet.balance}")

        # Update withdrawal record
        logger.info(f"models.py - Updating withdrawal request {self.id} status to 'approved'")
        self.status = "approved"
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "processed_at"])
        logger.info(f"models.py - WithdrawalRequest {self.id} approved for {self.user.username}, processed at: {self.processed_at}")
        print(f"[INFO] WithdrawalRequest {self.id} approved for {self.user.username}")

        # Safely handle transaction
        if transaction:
            logger.info(f"models.py - Updating existing transaction {transaction.reference} status to 'completed'")
            old_transaction_status = transaction.status
            transaction.status = "completed"
            transaction.save(update_fields=["status"])
            logger.info(f"models.py - Transaction {transaction.reference} status updated from '{old_transaction_status}' to 'completed'")
            print(f"[INFO] Existing transaction marked as completed: ref={transaction.reference}")
        else:
            logger.warning(f"models.py - No matching transaction found for withdrawal {self.id}. Creating new transaction record")
            print(f"[WARN] No matching transaction found. Auto-creating for {self.user.username}")
            try:
                new_transaction = Transaction.objects.create(
                    wallet=wallet,
                    amount=self.amount,
                    transaction_type="withdrawal",
                    status="completed",
                )
                logger.info(f"models.py - New transaction created successfully: {new_transaction.reference} for withdrawal {self.id}")
            except Exception as e:
                logger.error(f"models.py - Failed to create new transaction for withdrawal {self.id}: {str(e)}")
                print(f"[ERROR] Failed to create transaction: {str(e)}")
                # Continue anyway since the withdrawal was already processed

        logger.info(f"models.py - WithdrawalRequest.approve() completed successfully for withdrawal {self.id}")
        return True

    def reject(self):
        """Mark as rejected and update transaction."""
        logger.info(f"models.py - WithdrawalRequest.reject() called for user {self.user.username}, amount: {self.amount}")
        if self.status == "pending":
            self.status = "rejected"
            self.processed_at = timezone.now()
            self.save()
            logger.info(f"models.py - WithdrawalRequest rejected and saved")

            # Also update the transaction status
            transaction = Transaction.objects.filter(
                wallet__user=self.user, amount=self.amount, transaction_type="withdrawal"
            ).first()
            if transaction:
                transaction.status = "rejected"
                transaction.save()
                logger.info(f"models.py - Transaction status updated to rejected")
            else:
                logger.warning(f"models.py - No transaction found for withdrawal rejection")
            
class Discount(models.Model):
    pubg = models.IntegerField()
    codm = models.IntegerField()
    fortnite = models.IntegerField()
    freefire = models.IntegerField(default=0)
    apple = models.IntegerField()
    google = models.IntegerField()
    steam = models.IntegerField()
    playstation = models.IntegerField()

class Category(models.TextChoices):
    ESIM = 'esim', 'ESIM'
    ECOMMERCE = 'ecommerce', 'E-Commerce'
    GAMES = 'games', 'Games'
    GIFTCARDS = 'gift-cards', 'Gift Cards'

class Crypto(models.Model):
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)
    image = models.URLField(blank=True, null=True)

class Product(models.Model):
    name = models.CharField(max_length=50)
    image = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    discount = models.IntegerField(default=0, help_text="Discount percentage for the product")
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        logger.info(f"models.py - Product.save() called for product: {self.name}")
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
            logger.info(f"models.py - Generated slug: {self.slug}")
        super().save(*args, **kwargs)
        logger.info(f"models.py - Product.save() completed for product: {self.name}")

    def __str__(self):
        return self.name

class ProductTier(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="tiers")
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_currency = models.CharField(max_length=10, default="USD")

    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    @property
    def price_in_ghs(self):
        logger.info(f"models.py - ProductTier.price_in_ghs called for {self.product.name} - {self.name}")
        result = ExchangeRate.convert_to_ghs(self.price)
        logger.info(f"models.py - Price conversion: {self.price} {self.price_currency} -> {result} GHS")
        return result


class Trade(models.Model):
    product = models.CharField(max_length=50)
    amount = models.IntegerField(default=0)
    currency = models.CharField(max_length=10)
    card_code = models.CharField(max_length=50)
    card_image = models.FileField(upload_to='trade/cards/', null=True, blank=True)
    card_type = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    player_id = models.CharField(max_length=255, default='00')
    product = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.status}"
   
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('purchase', 'Purchase'),
        ('withdrawal', 'Withdrawal'),
        ('investment', 'Investment'),
        ('refund', 'Refund'),
        ('task_reward', 'Task Reward')
    ]

    order = models.ForeignKey(
        "Order", on_delete=models.SET_NULL, null=True, related_name="transaction"
    )
    wallet = models.ForeignKey("Wallet", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference = models.CharField(max_length=100, unique=True, blank=True)
    status = models.CharField(max_length=20, default='pending')
    raw_data = models.JSONField(default=dict, blank=True)  # restore
    wallet_applied = models.BooleanField(default=False)    # restore
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        logger.info(f"models.py - Transaction.save() called - type: {self.transaction_type}, amount: {self.amount}, wallet: {self.wallet.user.username}")
        if not self.reference:
            self.reference = str(uuid.uuid4())
            logger.info(f"models.py - Generated transaction reference: {self.reference}")
        result = super().save(*args, **kwargs)
        logger.info(f"models.py - Transaction.save() completed - ID: {self.id}, Reference: {self.reference}")
        return result

    def __str__(self):
        return f"{self.wallet.user.username} - {self.transaction_type} - GHS{self.amount} ({self.status})"

  
class InvestmentPlan(models.TextChoices):
    QUICK_RETURNS = "quick", "Quick Returns Plan"
    PREMIUM_RETURNS = "premium", "Premium Returns Plans"

class Investment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="investments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    plan = models.CharField(max_length=10, choices=InvestmentPlan.choices)
    daily_return = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField()
    last_checked = models.DateTimeField(default=now)
    status = models.CharField(
        max_length=10,
        choices=[("active", "Active"),
                ("completed", "Completed"),
                ("canceled", "Canceled")], default="active"
    )

    def is_active(self):
        """check if investment is still running"""
        logger.info(f"models.py - Investment.is_active() called for investment {self.id}")
        result = now() < self.end_date
        logger.info(f"models.py - Investment {self.id} active status: {result}")
        return result
    
    @staticmethod
    def user_has_active_investment(user, tier):
        logger.info(f"models.py - Investment.user_has_active_investment() called for user {user.username}, tier: {tier}")
        result = Investment.objects.filter(user=user, plan=tier, end_date__gt=now()).exists()
        logger.info(f"models.py - User {user.username} has active investment in tier {tier}: {result}")
        return result
    
    def calculate_earnings(self):
        """Returns total earnings based on daily returns"""
        logger.info(f"models.py - Investment.calculate_earnings() called for investment {self.id}")
        if self.status != "active":
            logger.info(f"models.py - Investment {self.id} not active, returning 0 earnings")
            return 0  # No earnings for completed or canceled investments

        elapsed_days = (now().date() - self.start_date.date()).days  # Use start_date, not last_checked
        logger.info(f"models.py - Investment {self.id} elapsed days: {elapsed_days}")
        if elapsed_days <= 0:
            logger.info(f"models.py - Investment {self.id} just started, returning 0 earnings")
            return 0  # No earnings if investment just started

        earnings = (self.amount * self.daily_return / 100) * elapsed_days
        logger.info(f"models.py - Investment {self.id} calculated earnings: {earnings}")
        return earnings  # Do NOT update last_checked
    
    def time_left(self):
        """Returns remaining time in days, hours, and minutes."""
        logger.info(f"models.py - Investment.time_left() called for investment {self.id}")
        remaining_time = self.end_date - now()
        if remaining_time.total_seconds() <= 0:
            logger.info(f"models.py - Investment {self.id} has ended")
            return {"days": 00, "hours": 00, "minutes": 00}  # Investment has ended

        days = remaining_time.days
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        result = {"days": f"{days:02d}",
                "hours": f"{hours:02d}", 
                "minutes": f"{minutes:02d}"}
        logger.info(f"models.py - Investment {self.id} time left: {result}")
        return result
    
    def check_completion(self):
        """Mark investment as completed if the durarion has ended"""
        logger.info(f"models.py - Investment.check_completion() called for investment {self.id}")
        if now() >= self.end_date and self.status == "active":
            self.status = "completed"
            self.save(update_fields=["status"])
            logger.info(f"models.py - Investment {self.id} marked as completed")
        else:
            logger.info(f"models.py - Investment {self.id} not yet completed")

    def claim_earnings(self):
        """Transfers earnings to the user wallet after investment completion"""
        logger.info(f"models.py - Investment.claim_earnings() called for investment {self.id}")

        total_earnings = self.calculate_earnings()
        logger.info(f"models.py - Total earnings calculated: {total_earnings}")

        wallet = Wallet.objects.get(user=self.user)
        total_earnings_in_ghs = ExchangeRate.convert_to_ghs(total_earnings)
        logger.info(f"models.py - Earnings converted to GHS: {total_earnings_in_ghs}")

        wallet.balance += total_earnings_in_ghs
        wallet.save(update_fields=['balance'])
        logger.info(f"models.py - Wallet balance updated. New balance: {wallet.balance}")

        Transaction.objects.create(
            wallet=wallet,
            amount=total_earnings_in_ghs,
            transaction_type="deposit",
            status="complete"
        )
        logger.info(f"models.py - Transaction created for earnings claim")

        self.status = "completed"
        self.save(update_fields=['status'])
        logger.info(f"models.py - Investment {self.id} marked as completed after earnings claim")

    
    def save(self, *args, **kwargs):
        logger.info(f"models.py - Investment.save() called for user {self.user.username}, plan: {self.plan}")
        if not self.end_date:
            self.end_date = self.start_date * timedelta(days=self.duration)
            logger.info(f"models.py - Investment end_date calculated: {self.end_date}")
        result = super().save(*args, **kwargs)
        logger.info(f"models.py - Investment.save() completed - ID: {self.id}")
        return result

class ReferralAmount(models.Model):
    purchase_reward = models.DecimalField(max_digits=10, decimal_places=2)
    signup_reward = models.DecimalField(max_digits=10, decimal_places=2)

class ReferralCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="referral_code")
    code = models.CharField(max_length=10, unique=True, blank=True)

    def save(self, *args, **kwargs):
        """Generate referral code if not set"""
        logger.info(f"models.py - ReferralCode.save() called for user {self.user.username}")
        if not self.code:
            self.code = str(uuid.uuid4())[:10].upper()  # Generate unique 10-character code
            logger.info(f"models.py - Generated referral code: {self.code}")
        result = super().save(*args, **kwargs)
        logger.info(f"models.py - ReferralCode.save() completed")
        return result

class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="referrals")
    referred_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="referred_by")
    created_at = models.DateTimeField(auto_now_add=True)
    earned_from_signup = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    earned_from_purchases = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    received_reward = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)

    def total_earnings(self):
        logger.info(f"models.py - Referral.total_earnings() called for referral {self.id}")
        result = self.earned_from_signup + self.earned_from_purchases
        logger.info(f"models.py - Referral {self.id} total earnings: {result}")
        return result

    @classmethod
    def get_total_earnings(cls, user):
        """Calculate total earnings for a referrer"""
        logger.info(f"models.py - Referral.get_total_earnings() called for user {user.username}")
        result = cls.objects.filter(referrer=user).aggregate(
            total_earned=Sum(F('earned_from_signup') + F('earned_from_purchases'))
        )['total_earned'] or 0
        logger.info(f"models.py - User {user.username} total referral earnings: {result}")
        return result

class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)
    device_info = models.TextField(blank=True, null=True)
    device_type=models.CharField(max_length=20, choices=[("Mobile", "Mobile"), ("Latop/Desktop", "Laptop/Desktop")], default="Laptop/Desktop")

    def __str__(self):
        return f"{self.user.username} - {self.device_type}- {self.timestamp}"

class BillBoardImage(models.Model):
    image1 = models.URLField(blank=True, null=True)
    image2 = models.URLField(blank=True, null=True)
    image3 = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Billboard Image"

class ExchangeRate(models.Model):
    currency = models.CharField(max_length=3, unique=True)
    rate_to_ghs = models.DecimalField(max_digits=10, decimal_places=4)

    @classmethod
    def convert_to_ghs(cls, amount, currency="USD"):
        """Converts an amount from USD to GHS before processing payments."""
        logger.info(f"models.py - ExchangeRate.convert_to_ghs() called - amount: {amount}, currency: {currency}")
        rate = cls.get_rate(currency=currency)
        result = round(amount * rate, 2)
        logger.info(f"models.py - Exchange rate conversion: {amount} {currency} -> {result} GHS (rate: {rate})")
        return result

    @classmethod
    def get_rate(cls, currency="USD"):
        logger.info(f"models.py - ExchangeRate.get_rate() called for currency: {currency}")
        rate_obj = cls.objects.filter(currency=currency).first()
        result = rate_obj.rate_to_ghs if rate_obj else 1
        logger.info(f"models.py - Exchange rate for {currency}: {result}")
        return result

class Task(models.Model):
    SOCIAL_MEDIA_CHOICES = [
        ('twitter', 'Twitter'),
        ('youtube', 'YouTube'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
    ]
    name = models.CharField(max_length=255)
    platform = models.CharField(max_length=20, choices=SOCIAL_MEDIA_CHOICES)
    url = models.URLField()
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_icon(self):
        """Returns the font awesome icons"""
        logger.info(f"models.py - Task.get_icon() called for task {self.name}")
        icons = {
            "youtube": "fab fa-youtube",
            "twitter": "fab fa-twitter",
            "instagram": "fab fa-instagram",
            "tiktok": "fab fa-tiktok"
        }

        result = icons.get(self.platform, "fas fas-question-circle")
        logger.info(f"models.py - Task {self.name} icon: {result}")
        return result

    def __str__(self):
        return f"{self.name} ({self.platform})"

class TaskCompletion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'task')

    def __str__(self):
        return f"{self.user.username} completed {self.task.name}"


class Stage(models.TextChoices):
    GROUP_STAGE = "group", "Group Stage"
    QUARTER_FINALS = "quarter", "Quarter Finals"  # fixed typo
    SEMI_FINALS = "semi", "Semi Finals"
    CHAMPIONSHIP_FINAL = "final", "Championship Final"

class ClashTournament(models.Model):
    player1 = models.CharField(max_length=100)  # Consider ForeignKey to Player
    player2 = models.CharField(max_length=100)  # Same here
    date = models.DateField(default=timezone.now)
    time = models.IntegerField(default=0000,help_text="Enter time as HHMM, e.g., 1330 for 1:30 PM")
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.GROUP_STAGE)

    def __str__(self):
        return f"{self.player1} vs {self.player2} - {self.get_stage_display()}"

    def get_time_display(self):
        logger.info(f"models.py - ClashTournament.get_time_display() called for tournament {self.id}")
        t = str(self.time).zfill(4)
        result = f"{t[:2]}:{t[2:]}"
        logger.info(f"models.py - Tournament {self.id} time display: {result}")
        return result
    

class BattleRoyaleTournament(models.Model):
    name = models.CharField(max_length=100, help_text="Battle royale tournament name")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class BattleRoyalePlayer(models.Model):
    player_name = models.CharField(max_length=100)
    kills = models.IntegerField(default=0)
    matches_played = models.IntegerField(default=0)
    country = CountryField(blank_label='(select country)')
    match = models.ForeignKey(BattleRoyaleTournament, on_delete=models.CASCADE, related_name='players')

    def __str__(self):
        return f"{self.player_name} - {self.country} - {self.kills} kills in {self.matches_played} matches"

class SquadTournament(models.Model):
    name = models.CharField(max_length=100, help_text="Squad tournament name")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SquadPlayer(models.Model):
    player = models.CharField(max_length=100)
    kills = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.player} - {self.kills} kills"

class Squad(models.Model):
    name = models.CharField(max_length=100, help_text="Squad name")
    players = models.ManyToManyField(SquadPlayer, related_name='squads')
    tournament = models.ForeignKey(SquadTournament, on_delete=models.CASCADE, related_name='squads')

    def __str__(self):
        return f"{self.name} - {self.tournament.name}"
    




























































class DataPurchase(models.Model):
    """
    Represents a user’s request to buy a data bundle.
    NOTE: Wallet is NOT deducted at creation time. Admin will approve/reject later.
    """
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("canceled", "Canceled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="data_purchases")
    beneficiary_number = models.CharField(max_length=20)         # the target phone number
    provider = models.CharField(max_length=20, default="mtn")    # e.g., mtn, vodafone, airteltigo
    bundle_size = models.CharField(max_length=20)                 # e.g., "1GB", "10GB"
    price_ghs = models.DecimalField(max_digits=10, decimal_places=2)  # final price in GHS
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    reference = models.CharField(max_length=100, unique=True, default=uuid.uuid4)  # for tracking
    notes = models.TextField(blank=True, null=True)                # optional admin/user notes

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)     # set when approved/rejected

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"DataPurchase #{self.id} - {self.user.username} - {self.status}"
    


    def approve(self):
        """
        Approve this data purchase:
        - Deduct wallet balance.
        - Mark as approved.
        - Create a Transaction record.
        """
        logger.info(f"models.py - DataPurchase.approve() called for {self.id} ({self.user.username})")

        # Prevent re-approval
        if self.status != "pending":
            logger.warning(f"models.py - DataPurchase {self.id} already processed (status={self.status})")
            return False

        # Try fetching wallet
        try:
            wallet = Wallet.objects.get(user=self.user)
            logger.info(f"models.py - Wallet found for user {self.user.username}: balance={wallet.balance}")
        except Wallet.DoesNotExist:
            logger.error(f"models.py - Wallet not found for user {self.user.username}")
            return False

        # Check sufficient balance
        if wallet.balance < self.price_ghs:
            logger.error(
                f"models.py - Insufficient funds for {self.user.username}: "
                f"wallet={wallet.balance}, price={self.price_ghs}"
            )
            self.status = "canceled"
            self.notes = "Insufficient wallet balance at approval time."
            self.processed_at = timezone.now()
            self.save(update_fields=["status", "notes", "processed_at"])
            return False

        # Deduct wallet and save
        old_balance = wallet.balance
        wallet.balance -= self.price_ghs
        wallet.save(update_fields=["balance"])
        logger.info(f"models.py - Wallet updated: {old_balance} -> {wallet.balance}")

        # Create transaction record
        Transaction.objects.create(
            wallet=wallet,
            amount=self.price_ghs,
            transaction_type="data_purchase",
            status="completed",
            raw_data={"bundle_size": self.bundle_size, "provider": self.provider},
        )
        logger.info(f"models.py - Transaction created for DataPurchase {self.id}")

        # Update purchase
        self.status = "approved"
        self.processed_at = timezone.now()
        self.save(update_fields=["status", "processed_at"])
        logger.info(f"models.py - DataPurchase {self.id} marked as approved")

        return True

def reject(self, reason="Rejected by admin"):
    """
    Reject a pending data purchase without touching wallet.
    """
    logger.info(f"models.py - DataPurchase.reject() called for {self.id} ({self.user.username})")

    if self.status != "pending":
        logger.warning(f"models.py - DataPurchase {self.id} cannot be rejected (status={self.status})")
        return False

    self.status = "rejected"
    self.notes = reason
    self.processed_at = timezone.now()
    self.save(update_fields=["status", "notes", "processed_at"])
    logger.info(f"models.py - DataPurchase {self.id} marked as rejected")

    return True

