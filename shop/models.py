from django.db import models
from django.db.models import Sum, F
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils.timezone import now
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
import uuid
# Create your models here.

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username}'s Wallet"

    def deposit(self, amount):
        """Credit user's wallet"""
        self.balance += Decimal(str(amount))
        self.save()

    def withdraw(self, amount):
        amount = Decimal(str(amount))
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False # Insufficient balance
    
    def deduct(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

    def add(self, amount):
        self.balance += amount
        self.save()

    def update_balance(self):
        """Caclculate earnings for all active investments and update the wallet balance"""
        investments = self.user.investments.filter(status="active")
        total_earnings = sum(investments.calculate_earnings() for investment in investments)
        if total_earnings > 0:
            self.balance += total_earnings
            self.save()
        for investment in investments:
            investment.check_completion

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
        """Deduct balance and mark as approved."""
        if self.status == "pending":
            wallet = Wallet.objects.get(user=self.user)
            transaction = Transaction.objects.filter(wallet=wallet, amount=self.amount, transaction_type="withdrawal").first()
            if transaction:
                transaction.status = "completed"
                transaction.save()
            if wallet.balance >= self.amount:
                wallet.balance -= self.amount
                wallet.save()
                
                self.status = "approved"
                self.processed_at = timezone.now()
                self.save()
                return True
        return False
    
    def reject(self):
        """Mark as rejected."""
        if self.status == "pending":
            self.status = "rejected"
            self.processed_at = timezone.now()
            self.save()
            
class Discount(models.Model):
    pubg = models.IntegerField()
    codm = models.IntegerField()
    fortnite = models.IntegerField()
    free_fire = models.IntegerField()
    apple = models.IntegerField()
    google = models.IntegerField()
    steam = models.IntegerField()
    play_station = models.IntegerField()

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('purchase', 'Purchase'),
        ('withdrawal', 'Withdrawal'),
        ('investment', 'Investment'),
        ('refund', 'Refund'),
        ('task_reward', 'Task Reward')
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type =models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = str(uuid.uuid4())
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.wallet.user.username} - {self.transaction_type} - GHS{self.amount}"

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
        return now() < self.end_date
    
    @staticmethod
    def user_has_active_investment(user, tier):
        return Investment.objects.filter(user=user, plan=tier, end_date__gt=now()).exists
    
    def calculate_earnings(self):
        """Returns total earnings based on daily returns"""
        if self.status != "active":
            return 0  # No earnings for completed or canceled investments

        elapsed_days = (now().date() - self.start_date.date()).days  # Use start_date, not last_checked
        if elapsed_days <= 0:
            return 0  # No earnings if investment just started

        earnings = (self.amount * self.daily_return / 100) * elapsed_days
        return earnings  # Do NOT update last_checked
    
    def time_left(self):
        """Returns remaining time in days, hours, and minutes."""
        remaining_time = self.end_date - now()
        if remaining_time.total_seconds() <= 0:
            return {"days": 00, "hours": 00, "minutes": 00}  # Investment has ended

        days = remaining_time.days
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        return {"days": f"{days:02d}",
                "hours": f"{hours:02d}", 
                "minutes": f"{minutes:02d}"}
    
    def check_completion(self):
        """Mark investment as completed if the durarion has ended"""
        if now() >= self.end_date and self.status == "active":
            self.status = "completed"
            self.save(update_fields=["status"])

    def claim_earnings(self):
        """Transfers earnings to the user wallet after investment completion"""

        total_earnings = self.calculate_earnings()

        wallet = Wallet.objects.get(user=self.user)
        total_earnings_in_ghs = ExchangeRate.convert_to_ghs(total_earnings)
        wallet.balance += total_earnings_in_ghs
        wallet.save(update_fields=['balance'])

        Transaction.objects.create(
            wallet=wallet,
            amount=total_earnings_in_ghs,
            transaction_type="deposit",
            status="complete"
        )
        self.status = "completed"
        self.save(update_fields=['status'])

    
    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.start_date * timedelta(days=self.duration)
        super().save(*args, **kwargs)

class ReferralCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="referral_code")
    code = models.CharField(max_length=10, unique=True, blank=True)

    def save(self, *args, **kwargs):
        """Generate referral code if not set"""
        if not self.code:
            self.code = str(uuid.uuid4())[:10].upper()  # Generate unique 10-character code
        super().save(*args, **kwargs)

class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="referrals")
    referred_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="referred_by")
    created_at = models.DateTimeField(auto_now_add=True)
    earned_from_signup = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    earned_from_purchases = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)

    def total_earnings(self):
        return self.earned_from_signup + self.earned_from_purchases

    @classmethod
    def get_total_earnings(cls, user):
        """Calculate total earnings for a referrer"""
        return cls.objects.filter(referrer=user).aggregate(
            total_earned=Sum(F('earned_from_signup') + F('earned_from_purchases'))
        )['total_earned'] or 0


class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)
    device_info = models.TextField(blank=True, null=True)
    device_type=models.CharField(max_length=20, choices=[("Mobile", "Mobile"), ("Latop/Desktop", "Laptop/Desktop")], default="Laptop/Desktop")

    def __str__(self):
        return f"{self.user.username} - {self.device_type}- {self.timestamp}"

class BillBoardImage(models.Model):
    image_url = models.ImageField(upload_to="billboard_images/")

    def __str__(self):
        return f"Billboard Image"

class ExchangeRate(models.Model):
    currency = models.CharField(max_length=3, unique=True)
    rate_to_ghs = models.DecimalField(max_digits=10, decimal_places=4)

    @classmethod
    def convert_to_ghs(cls, amount, currency="USD"):
        """Converts an amount from USD to GHS before processing payments."""
        rate = cls.get_rate(currency=currency)
        return round(amount * rate, 2)

    @classmethod
    def get_rate(cls, currency="USD"):
        rate_obj = cls.objects.filter(currency=currency).first()

        return rate_obj.rate_to_ghs if rate_obj else 1

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
        icons = {
            "youtube": "fab fa-youtube",
            "twitter": "fab fa-twitter",
            "instagram": "fab fa-instagram",
            "tiktok": "fab fa-tiktok"
        }

        return icons.get(self.platform, "fas fas-question-circle")

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

