import logging
from typing import Optional, Dict, Any
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from django.db import transaction as db_transaction
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from shop.models import Transaction, Wallet

User = get_user_model()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
TX_STATUS_COMPLETED = "completed"
TX_STATUS_PENDING   = "pending"
TX_STATUS_FAILED    = "failed"
VALID_STATUSES = {TX_STATUS_COMPLETED, TX_STATUS_PENDING, TX_STATUS_FAILED}

TX_TYPE_DEPOSIT     = "deposit"
TX_TYPE_WITHDRAWAL  = "withdrawal"
TX_TYPE_PURCHASE    = "purchase"
TX_TYPE_INVESTMENT  = "investment"
TX_TYPE_REFUND      = "refund"
TX_TYPE_TASK_REWARD = "task_reward"
VALID_TYPES = {
    TX_TYPE_DEPOSIT,
    TX_TYPE_WITHDRAWAL,
    TX_TYPE_PURCHASE,
    TX_TYPE_INVESTMENT,
    TX_TYPE_REFUND,
    TX_TYPE_TASK_REWARD,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _q2(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

def _coerce_raw_data(raw_data: Optional[Any]) -> Optional[Dict[str, Any]]:
    if raw_data is None:
        return None
    if isinstance(raw_data, dict):
        return raw_data
    return {"raw": str(raw_data)}

def _should_apply_wallet_change(prev_status: str, new_status: str) -> bool:
    return prev_status != TX_STATUS_COMPLETED and new_status == TX_STATUS_COMPLETED

# ---------------------------------------------------------------------------
# Transaction Service
# ---------------------------------------------------------------------------
class TransactionService:
    """Manages creation, update, and wallet sync of transactions safely."""

    @staticmethod
    @db_transaction.atomic
    def record_transaction(
        *,
        user: AbstractUser,
        amount: Decimal,
        transaction_type: str,
        reference: str,
        status: str = TX_STATUS_PENDING,
        raw_data: Optional[Dict[str, Any]] = None,
        update_wallet: bool = False,
    ) -> Transaction:
        """
        Create or update a transaction safely.
        NOTE: Withdrawals are now managed manually (no external overwrite).
        """
        if transaction_type == TX_TYPE_WITHDRAWAL:
            logger.info(f"[TX][RECORD] Skipped external record for withdrawal Ref={reference}")
            return TransactionService.get_by_reference(reference)

        # --- normal deposits, etc ---
        if transaction_type not in VALID_TYPES:
            logger.warning(f"[TX][RECORD] Ref={reference} | Unknown type={transaction_type}")
        if status not in VALID_STATUSES:
            logger.warning(f"[TX][RECORD] Ref={reference} | Unknown status={status}")

        try:
            amount = _q2(Decimal(amount))
        except (InvalidOperation, TypeError):
            logger.exception(f"[TX][RECORD] Ref={reference} | Invalid amount={amount}")
            raise

        wallet, _ = Wallet.objects.get_or_create(user=user)

        try:
            tx = Transaction.objects.select_for_update().get(reference=reference)
            prev_status = tx.status
            tx.amount = amount
            tx.transaction_type = transaction_type
            tx.status = status
            tx.wallet = wallet
            tx.save(update_fields=["wallet", "amount", "transaction_type", "status", "updated_at"])
            logger.info(f"[TX][UPDATE] Ref={reference} | {prev_status} → {status}")
        except ObjectDoesNotExist:
            prev_status = TX_STATUS_PENDING
            tx = Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type=transaction_type,
                reference=reference,
                status=status,
                created_at=timezone.now(),
                wallet_applied=False,
            )
            logger.info(f"[TX][CREATE] Ref={reference} | Created | Status={status}")

        safe_raw = _coerce_raw_data(raw_data)
        if safe_raw:
            tx.raw_data = safe_raw
            tx.save(update_fields=["raw_data"])

        if update_wallet and _should_apply_wallet_change(prev_status, status):
            TransactionService._apply_wallet_effect(tx)

        return tx

    @staticmethod
    def get_by_reference(reference: str):
        try:
            tx = Transaction.objects.get(reference=reference)
            logger.debug("[TX][GET] Ref=%s | Found id=%s", reference, tx.id)
            return tx
        except Transaction.DoesNotExist:
            logger.warning("[TX][GET] Ref=%s | Not found", reference)
            return None

    @staticmethod
    def mark_success(reference: str, update_wallet: bool = False):
        return TransactionService.update_transaction_status(
            reference=reference,
            new_status=TX_STATUS_COMPLETED,
            update_wallet=update_wallet,
        )

    @staticmethod
    def mark_failed(reference: str):
        return TransactionService.update_transaction_status(
            reference=reference,
            new_status=TX_STATUS_FAILED,
        )

    @staticmethod
    def mark_pending(reference: str):
        return TransactionService.update_transaction_status(
            reference=reference,
            new_status=TX_STATUS_PENDING,
        )

    @staticmethod
    @db_transaction.atomic
    def update_transaction_status(
        reference: str,
        new_status: str,
        raw_data: Optional[Dict[str, Any]] = None,
        update_wallet: bool = False,
    ) -> Optional[Transaction]:
        try:
            tx = Transaction.objects.select_for_update().get(reference=reference)
        except ObjectDoesNotExist:
            logger.warning(f"[TX][SET_STATUS] Ref={reference} | Not found")
            return None

        # 🚫 skip all withdrawal updates from any background service
        if tx.transaction_type == TX_TYPE_WITHDRAWAL:
            logger.info(f"[TX][SET_STATUS] Skipped withdrawal Ref={reference} (manual mode)")
            return tx

        prev_status = tx.status
        if prev_status == new_status:
            logger.info(f"[TX][SET_STATUS] Ref={reference} | No change ({new_status})")
            return tx

        tx.status = new_status
        safe_raw = _coerce_raw_data(raw_data)
        if safe_raw:
            tx.raw_data = safe_raw
        tx.save(update_fields=["status", "raw_data", "updated_at"])
        logger.info(f"[TX][SET_STATUS] Ref={reference} | {prev_status} → {new_status}")

        if update_wallet and _should_apply_wallet_change(prev_status, new_status):
            TransactionService._apply_wallet_effect(tx)
        return tx

    @staticmethod
    def _apply_wallet_effect(tx: Transaction) -> None:
        wallet = tx.wallet
        amount = _q2(tx.amount)

        if getattr(tx, "wallet_applied", False):
            logger.info(f"[TX][WALLET_SYNC] Ref={tx.reference} | Skip duplicate wallet credit")
            return

        if tx.transaction_type == TX_TYPE_DEPOSIT:
            wallet.deposit(amount)
            logger.info(f"[TX][WALLET][DEPOSIT] Ref={tx.reference} | +{amount}")
        elif tx.transaction_type == TX_TYPE_WITHDRAWAL:
            # still allowed manually if triggered by admin (not Moolre)
            logger.info(f"[TX][WALLET][WITHDRAW] Ref={tx.reference} | manual deduction only")
        wallet.save(update_fields=["balance"])

        tx.wallet_applied = True
        tx.save(update_fields=["wallet_applied", "updated_at"])
        logger.info(f"[TX][WALLET_SYNC] Ref={tx.reference} | Wallet updated once safely")




import logging
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from shop.models import Transaction, Wallet
from payments.services.transaction_service import (
    TransactionService,
    TX_STATUS_PENDING,
    TX_STATUS_COMPLETED,
    TX_STATUS_FAILED,
    TX_TYPE_DEPOSIT,
    TX_TYPE_WITHDRAWAL,
)
from django.db.models import Q

logger = logging.getLogger(__name__)

class TransactionRefresher:
    """
    Reconciles only DEPOSITS via Moolre.
    Withdrawals are skipped (manual approval only).
    """

    @staticmethod
    def refresh_account_balance(user: AbstractUser, account_number: str):
        from payments.services import moolre_service

        refreshed, completed, failed = 0, 0, 0
        window = timezone.now() - timedelta(days=7)

        pending_txs = Transaction.objects.filter(
            wallet__user=user,
            status=TX_STATUS_PENDING,
            created_at__gte=window
        )

        logger.info("[TX][REFRESH_USER] User=%s | Pending=%d", user.username, pending_txs.count())

        for tx in pending_txs:
            refreshed += 1

            # 🚫 skip withdrawals completely
            if tx.transaction_type == TX_TYPE_WITHDRAWAL:
                logger.info("[TX][REFRESH_USER] Skipped withdrawal Ref=%s (manual approval)", tx.reference)
                continue

            try:
                result = moolre_service.check_payment_status(user, account_number, tx.reference)
                tx_data = result.get("data", {}) or {}
                txstatus = str(tx_data.get("txstatus", "0"))
                status_map = {"0": TX_STATUS_PENDING, "1": TX_STATUS_COMPLETED, "2": TX_STATUS_FAILED}
                new_status = status_map.get(txstatus, TX_STATUS_PENDING)

                if new_status == TX_STATUS_COMPLETED:
                    completed += 1
                    TransactionService.update_transaction_status(
                        reference=tx.reference,
                        new_status=TX_STATUS_COMPLETED,
                        raw_data=result,
                        update_wallet=True
                    )
                elif new_status == TX_STATUS_FAILED:
                    failed += 1
                    TransactionService.update_transaction_status(
                        reference=tx.reference,
                        new_status=TX_STATUS_FAILED,
                        raw_data=result,
                        update_wallet=False
                    )
                else:
                    logger.info("[TX][REFRESH_USER] Ref=%s still pending", tx.reference)
            except Exception as e:
                logger.exception("[TX][REFRESH_USER] Ref=%s error: %s", tx.reference, e)

        summary = {
            "user": user.username,
            "checked": refreshed,
            "completed": completed,
            "failed": failed,
            "timestamp": timezone.now().isoformat(),
        }
        logger.info("[TX][REFRESH_USER][SUMMARY] %s", summary)
        return summary

    @staticmethod
    def refresh_pending_transactions(days: int = 7):
        from payments.services import moolre_service

        refreshed, completed, failed = 0, 0, 0
        window = timezone.now() - timedelta(days=days)

        pending_txs = Transaction.objects.filter(
            status=TX_STATUS_PENDING,
            created_at__gte=window
        ).select_related("wallet__user")

        logger.info("[TX][REFRESH_ALL] Pending count=%d", pending_txs.count())

        for tx in pending_txs:
            refreshed += 1
            user = tx.wallet.user

            # 🚫 ignore all withdrawals
            if tx.transaction_type == TX_TYPE_WITHDRAWAL:
                logger.info("[TX][REFRESH_ALL] Skipped withdrawal Ref=%s (manual approval only)", tx.reference)
                continue

            try:
                account_number = Wallet.objects.filter(user=user).values_list("account_number", flat=True).first()
                if not account_number:
                    continue

                result = moolre_service.check_payment_status(user, account_number, tx.reference)
                tx_data = result.get("data", {}) or {}
                txstatus = str(tx_data.get("txstatus", "0"))
                status_map = {"0": TX_STATUS_PENDING, "1": TX_STATUS_COMPLETED, "2": TX_STATUS_FAILED}
                new_status = status_map.get(txstatus, TX_STATUS_PENDING)

                if new_status == TX_STATUS_COMPLETED:
                    completed += 1
                    TransactionService.update_transaction_status(
                        reference=tx.reference,
                        new_status=TX_STATUS_COMPLETED,
                        raw_data=result,
                        update_wallet=True
                    )
                elif new_status == TX_STATUS_FAILED:
                    failed += 1
                    TransactionService.update_transaction_status(
                        reference=tx.reference,
                        new_status=TX_STATUS_FAILED,
                        raw_data=result,
                        update_wallet=False
                    )
            except Exception as e:
                logger.exception("[TX][REFRESH_ALL] Ref=%s error: %s", tx.reference, e)

        summary = {
            "checked": refreshed,
            "completed": completed,
            "failed": failed,
            "remaining": refreshed - completed - failed,
            "timestamp": timezone.now().isoformat(),
        }
        logger.info("[TX][REFRESH_ALL][SUMMARY] %s", summary)
        return summary
