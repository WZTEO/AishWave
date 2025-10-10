import logging
from typing import Optional, Dict, Any, Tuple
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from django.db import transaction as db_transaction
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser


# from payments.services.moolre_service import check_payment_status, check_transfer_status
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
# Utility helpers
# ---------------------------------------------------------------------------
def _q2(value: Decimal) -> Decimal:
    """Round and quantize to 2 decimal places."""
    return value.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

def _coerce_raw_data(raw_data: Optional[Any]) -> Optional[Dict[str, Any]]:
    """Ensure raw_data is safely serializable to JSON."""
    if raw_data is None:
        return None
    if isinstance(raw_data, dict):
        return raw_data
    return {"raw": str(raw_data)}

def _should_apply_wallet_change(prev_status: str, new_status: str) -> bool:
    """Wallet update allowed only when moving into COMPLETED for the first time."""
    return prev_status != TX_STATUS_COMPLETED and new_status == TX_STATUS_COMPLETED

# ---------------------------------------------------------------------------
# Transaction Service
# ---------------------------------------------------------------------------
class TransactionService:
    """
    Centralized transaction manager for deposits, withdrawals, and wallet sync.
    Ensures atomic, idempotent updates and guards against double-crediting.
    """


    # -------------------------------------------------------------------
    # CREATE OR UPDATE TRANSACTION
    # -------------------------------------------------------------------
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

        # Validate
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
            created = False
            tx.amount = amount
            tx.transaction_type = transaction_type
            tx.status = status
            tx.wallet = wallet
            tx.save(update_fields=["wallet", "amount", "transaction_type", "status", "updated_at"])
            logger.info(f"[TX][UPDATE] Ref={reference} | {prev_status} → {status}")
        except ObjectDoesNotExist:
            prev_status = TX_STATUS_PENDING
            created = True
            tx = Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type=transaction_type,
                reference=reference,
                status=status,
                created_at=timezone.now(),
                wallet_applied=False,   # ✅ add this field to your model if not present
            )
            logger.info(f"[TX][CREATE] Ref={reference} | Created | Status={status}")

        # Raw data audit
        safe_raw = _coerce_raw_data(raw_data)
        if safe_raw:
            tx.raw_data = safe_raw
            tx.save(update_fields=["raw_data"])

        # Wallet effect only on first completion
        if update_wallet and _should_apply_wallet_change(prev_status, status):
            TransactionService._apply_wallet_effect(tx)
        elif update_wallet:
            logger.info(f"[TX][WALLET_SYNC] Ref={reference} | Skipped (prev={prev_status} → new={status})")

        return tx
    
    # -------------------------------------------------------------------
    # FETCH / LOOKUP
    # -------------------------------------------------------------------
    @staticmethod
    def get_by_reference(reference: str):
     """
     Retrieve a transaction safely by its unique reference.
      Returns None if not found.
     """
     try:
        tx = Transaction.objects.get(reference=reference)
        logger.debug("[TX][GET] Ref=%s | Found id=%s", reference, tx.id)
        return tx
     except Transaction.DoesNotExist:
        logger.warning("[TX][GET] Ref=%s | Not found", reference)
        return None
    
        # -------------------------------------------------------------------
    # STATUS HELPERS (backward-compatible with old code)
    # -------------------------------------------------------------------
    @staticmethod
    def mark_success(reference: str, update_wallet: bool = False):
        """
        Mark a transaction as completed (idempotent).
        Optionally triggers wallet update on first completion.
        """
        return TransactionService.update_transaction_status(
            reference=reference,
            new_status=TX_STATUS_COMPLETED,
            raw_data=None,
            update_wallet=update_wallet,
        )

    @staticmethod
    def mark_failed(reference: str):
        """Mark a transaction as failed."""
        return TransactionService.update_transaction_status(
            reference=reference,
            new_status=TX_STATUS_FAILED,
            raw_data=None,
            update_wallet=False,
        )

    @staticmethod
    def mark_pending(reference: str):
        """Mark a transaction as pending."""
        return TransactionService.update_transaction_status(
            reference=reference,
            new_status=TX_STATUS_PENDING,
            raw_data=None,
            update_wallet=False,
        )



    # -------------------------------------------------------------------
    # STATUS UPDATES
    # -------------------------------------------------------------------
    @staticmethod
    @db_transaction.atomic
    def update_transaction_status(
        reference: str,
        new_status: str,
        raw_data: Optional[Dict[str, Any]] = None,
        update_wallet: bool = False,
    ) -> Optional[Transaction]:

        if new_status not in VALID_STATUSES:
            logger.warning(f"[TX][SET_STATUS] Ref={reference} | Invalid status={new_status}")

        try:
            tx = Transaction.objects.select_for_update().get(reference=reference)
        except ObjectDoesNotExist:
            logger.warning(f"[TX][SET_STATUS] Ref={reference} | Not found")
            return None

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

    # -------------------------------------------------------------------
    # INTERNAL WALLET EFFECTS (Idempotent)
    # -------------------------------------------------------------------
    @staticmethod
    def _apply_wallet_effect(tx: Transaction) -> None:
        """Apply a wallet mutation once when entering 'completed'."""
        wallet = tx.wallet
        amount = _q2(tx.amount)

        # ✅ Skip if already applied before
        if getattr(tx, "wallet_applied", False):
            logger.info(f"[TX][WALLET_SYNC] Ref={tx.reference} | Skip duplicate wallet credit")
            return

        if tx.transaction_type == TX_TYPE_DEPOSIT:
            wallet.deposit(amount)
            logger.info(f"[TX][WALLET][DEPOSIT] Ref={tx.reference} | +{amount}")
        elif tx.transaction_type == TX_TYPE_WITHDRAWAL:
            if wallet.balance >= amount:
                wallet.withdraw(amount)
                logger.info(f"[TX][WALLET][WITHDRAW] Ref={tx.reference} | -{amount}")
            else:
                logger.error(f"[TX][WALLET][WITHDRAW][INSUFFICIENT] Ref={tx.reference} | Balance={wallet.balance}")

        tx.wallet_applied = True
        tx.save(update_fields=["wallet_applied", "updated_at"])
        wallet.save(update_fields=["balance"])
        logger.info(f"[TX][WALLET_SYNC] Ref={tx.reference} | Wallet updated once safely")







# -------------------------------------------------------------------
# REFRESHERS / RECONCILIATION
# -------------------------------------------------------------------
from django.db.models import Q
from datetime import timedelta


class TransactionRefresher:
    """
    Handles automatic or manual reconciliation of transactions
    with Moolre’s servers — both for deposits and withdrawals.
    """

    @staticmethod
    def refresh_account_balance(user: AbstractUser, account_number: str) -> Dict[str, Any]:
        """
        Re-check all pending deposits & withdrawals for a user.
        Updates wallet balances if any are completed.
        """
        from payments.services import moolre_service  # ✅ lazy import added here

        refreshed, completed, failed = 0, 0, 0
        now = timezone.now()
        window = now - timedelta(days=7)

        pending_txs = Transaction.objects.filter(
            wallet__user=user,
            status=TX_STATUS_PENDING,
            created_at__gte=window
        )

        logger.info("[TX][REFRESH_USER] User=%s | Pending=%d", user.username, pending_txs.count())

        for tx in pending_txs:
            refreshed += 1
            try:
                if tx.transaction_type == TX_TYPE_DEPOSIT:
                    result = moolre_service.check_payment_status(user, account_number, tx.reference)
                elif tx.transaction_type == TX_TYPE_WITHDRAWAL:
                    result = moolre_service.check_transfer_status(user, account_number, tx.reference)
                else:
                    continue

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
                    logger.info(
                        "[TX][REFRESH_USER] Ref=%s | Still pending", tx.reference
                    )

            except Exception as e:
                logger.exception(
                    "[TX][REFRESH_USER] Ref=%s | Error during status refresh: %s",
                    tx.reference, str(e)
                )

        summary = {
            "user": user.username,
            "checked": refreshed,
            "completed": completed,
            "failed": failed,
            "timestamp": timezone.now().isoformat(),
        }

        logger.info("[TX][REFRESH_USER][SUMMARY] %s", summary)
        return summary

    # -----------------------------------------------------------------
    @staticmethod
    def refresh_pending_transactions(days: int = 7) -> Dict[str, Any]:
        """
        Re-check all pending transactions system-wide.
        To be run by admin or cron job (e.g., every 30 min).

        It reconciles both deposits and withdrawals.
        """
        refreshed, completed, failed = 0, 0, 0
        now = timezone.now()
        window = now - timedelta(days=days)

        pending_txs = Transaction.objects.filter(
            status=TX_STATUS_PENDING,
            created_at__gte=window,
        ).select_related("wallet__user")

        logger.info("[TX][REFRESH_ALL] Pending count=%d", pending_txs.count())

        for tx in pending_txs:
            refreshed += 1
            try:
                user = tx.wallet.user
                account_number = Wallet.objects.filter(user=user).values_list("account_number", flat=True).first()
                if not account_number:
                    logger.warning(
                        "[TX][REFRESH_ALL] Ref=%s | Missing account number | User=%s",
                        tx.reference, user.username
                    )
                    continue

                if tx.transaction_type == TX_TYPE_DEPOSIT:
                   result = moolre_service.check_payment_status(user, account_number, tx.reference)
                elif tx.transaction_type == TX_TYPE_WITHDRAWAL:
                   result = moolre_service.check_transfer_status(user, account_number, tx.reference)
            
                else:
                    logger.debug(
                        "[TX][REFRESH_ALL] Ref=%s | Skip type=%s",
                        tx.reference, tx.transaction_type
                    )
                    continue

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
                logger.exception("[TX][REFRESH_ALL] Ref=%s | Error: %s", tx.reference, str(e))

        summary = {
            "checked": refreshed,
            "completed": completed,
            "failed": failed,
            "remaining": refreshed - completed - failed,
            "timestamp": timezone.now().isoformat(),
        }
        logger.info("[TX][REFRESH_ALL][SUMMARY] %s", summary)
        return summary
