"""
Moolre API Service Layer
------------------------
Handles all interactions with Moolre’s REST API for:
 - Validation (account name check)
 - Transfers (outgoing payouts)
 - Payments (incoming deposits)
Each method is idempotent and integrated with TransactionService.
"""

import os
import json
import uuid
import logging
import requests
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from typing import Dict, Any, Optional

from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from payments.services.transaction_service import TransactionService
from shop.models import Wallet

# -------------------------------------------------------------------
# LOGGER CONFIGURATION
# -------------------------------------------------------------------
logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    )

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------
MOOLRE_BASE = os.getenv("MOOLRE_API_BASE_URL", "https://api.moolre.com")

HEADERS_PRIVATE = {
    "Content-Type": "application/json",
    "X-API-USER": os.getenv("MOOLRE_API_USER"),
    "X-API-KEY": os.getenv("MOOLRE_API_KEY"),
}

HEADERS_PUBLIC = {
    "Content-Type": "application/json",
    "X-API-USER": os.getenv("MOOLRE_API_USER"),
    "X-API-PUBKEY": os.getenv("MOOLRE_API_PUBKEY"),
}

# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------
def _build_url(endpoint: str) -> str:
    """Combine base URL with endpoint."""
    return f"{MOOLRE_BASE.rstrip('/')}/{endpoint.lstrip('/')}"

def _quantize(amount: Any) -> Decimal:
    """Safely convert to Decimal(0.01) precision."""
    try:
        return Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    except (InvalidOperation, TypeError):
        return Decimal("0.00")

def _safe_json(resp: requests.Response) -> Dict[str, Any]:
    """Ensure valid JSON dict for any HTTP response."""
    try:
        return resp.json()
    except json.JSONDecodeError:
        logger.error("[MOOLRE][SAFE_JSON] Invalid JSON (%s): %s",
                     resp.status_code, resp.text[:300])
        return {"status": 0, "message": f"Invalid or empty JSON ({resp.status_code})"}

# -------------------------------------------------------------------
# VALIDATION
# -------------------------------------------------------------------
def validate_recipient_name(
    account_number: str,
    receiver_number: str,
    channel: int,
    currency: str = "GHS",
    sublistid: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate recipient name for bank or mobile account.
    """
    url = _build_url("open/transact/validate")
    payload: Dict[str, Any] = {
        "type": 1,
        "receiver": receiver_number,
        "channel": channel,
        "currency": currency,
        "accountnumber": account_number,
    }
    if channel == 2 and sublistid:
        payload["sublistid"] = str(sublistid)

    try:
        logger.info("[MOOLRE][VALIDATE] Receiver=%s | Channel=%s", receiver_number, channel)
        r = requests.post(url, json=payload, headers=HEADERS_PRIVATE, timeout=15)
        data = _safe_json(r)
        if data.get("status") == 1:
            logger.info("[MOOLRE][VALIDATE] ✅ Success | %s", data.get("data"))
        else:
            logger.warning("[MOOLRE][VALIDATE] ❌ Failed | %s", data.get("message"))
        return data
    except requests.RequestException as e:
        logger.exception("[MOOLRE][VALIDATE] Network error: %s", e)
        return {"status": 0, "message": str(e)}

# -------------------------------------------------------------------
# TRANSFERS (OUTGOING)
# -------------------------------------------------------------------
def initiate_transfer(
    *,
    user: AbstractUser,
    account_number: str,
    receiver: str,
    amount: float,
    channel: int,
    reference: str,
    currency: str = "GHS",
    externalref: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send money (payout) from Moolre wallet to recipient (bank/MoMo).
    """
    url = _build_url("open/transact/transfer")
    externalref = externalref or f"tr_{uuid.uuid4().hex[:12]}"
    amt = _quantize(amount)

    payload: Dict[str, Any] = {
        "type": 1,
        "channel": channel,
        "currency": currency,
        "amount": float(amt),
        "receiver": receiver,
        "externalref": externalref,
        "reference": reference or f"Transfer {externalref}",
        "accountnumber": account_number,
    }

    logger.info("[MOOLRE][TRANSFER] ▶ Ref=%s | Amount=%.2f | Receiver=%s | Channel=%s",
                externalref, amt, receiver, channel)

    try:
        r = requests.post(url, json=payload, headers=HEADERS_PRIVATE, timeout=20)
        data = _safe_json(r)
        tx_data = data.get("data", {}) or {}
        txstatus = int(tx_data.get("txstatus", 0))
        status_map = {0: "pending", 1: "completed", 2: "failed"}
        status = status_map.get(txstatus, "pending")

        TransactionService.record_transaction(
            user=user,
            amount=amt,
            transaction_type="withdrawal",
            reference=externalref,
            status=status,
            raw_data=data,
        )
        logger.info("[MOOLRE][TRANSFER] Recorded transaction %s | Status=%s", externalref, status)
        return data

    except requests.RequestException as e:
        logger.exception("[MOOLRE][TRANSFER] ❌ Error: %s", e)
        return {"status": 0, "message": str(e)}

def check_transfer_status(
    user: AbstractUser,
    account_number: str,
    identifier: str,
    by: str = "external"
) -> Dict[str, Any]:
    """
    Re-query transfer status and sync Transaction model.
    """
    url = _build_url("open/transact/status")
    payload = {
        "type": 1,
        "idtype": 1 if by == "external" else 2,
        "id": identifier,
        "accountnumber": account_number,
    }

    logger.info("[MOOLRE][TRANSFER_STATUS] 🔎 Ref=%s", identifier)
    try:
        r = requests.post(url, json=payload, headers=HEADERS_PRIVATE, timeout=15)
        data = _safe_json(r)
        tx_data = data.get("data", {}) or {}
        txstatus = int(tx_data.get("txstatus", 0))
        status_map = {0: "pending", 1: "completed", 2: "failed"}
        status = status_map.get(txstatus, "pending")

        TransactionService.record_transaction(
            user=user,
            amount=_quantize(tx_data.get("amount", 0)),
            transaction_type="withdrawal",
            reference=identifier,
            status=status,
            raw_data=data,
        )

        logger.info("[MOOLRE][TRANSFER_STATUS] Ref=%s | Status=%s", identifier, status)
        return data

    except requests.RequestException as e:
        logger.exception("[MOOLRE][TRANSFER_STATUS] ❌ Error: %s", e)
        return {"status": 0, "message": str(e)}

# -------------------------------------------------------------------
# PAYMENTS (INCOMING)
# -------------------------------------------------------------------
def initiate_payment(
    *,
    user: AbstractUser,
    payer: str,
    amount: float,
    account_number: str,
    external_ref: str,
    reference: str = "Payment Request",
    channel: int = 13,
    currency: str = "GHS",
    otpcode: str = ""
) -> Dict[str, Any]:
    """
    Initiate a mobile money payment (collection).
    """
    url = _build_url("open/transact/payment")
    amt = _quantize(amount)

    payload: Dict[str, Any] = {
        "type": 1,
        "channel": channel,
        "currency": currency,
        "payer": payer,
        "amount": float(amt),
        "externalref": external_ref,
        "otpcode": otpcode or "",
        "reference": reference,
        "accountnumber": account_number,
    }

    logger.info("[MOOLRE][PAYMENT] ▶ Payer=%s | Amount=%.2f | Ref=%s | Channel=%s",
                payer, amt, external_ref, channel)

    try:
        r = requests.post(url, json=payload, headers=HEADERS_PUBLIC, timeout=20)
        data = _safe_json(r)
        code = data.get("code", "")
        requires_otp = code == "TP14"

        TransactionService.record_transaction(
            user=user,
            amount=amt,
            transaction_type="deposit",
            reference=external_ref,
            status="pending",
            raw_data=data,
        )
        logger.info("[MOOLRE][PAYMENT] Recorded transaction %s | Requires_OTP=%s",
                    external_ref, requires_otp)
        data["requires_otp"] = requires_otp
        return data

    except requests.RequestException as e:
        logger.exception("[MOOLRE][PAYMENT] ❌ Error: %s", e)
        return {"status": 0, "message": str(e)}

def check_payment_status(user: AbstractUser, account_number: str, reference: str, by: str = "external") -> Dict[str, Any]:
    """
    Re-check incoming payment status and update wallet + transaction safely.
    """
    url = _build_url("open/transact/status")
    payload = {
        "type": 1,
        "idtype": 1 if by == "external" else 2,
        "id": reference,
        "accountnumber": account_number,
    }

    logger.info("[MOOLRE][PAYMENT_STATUS] 🔍 Ref=%s", reference)
    try:
        r = requests.post(url, json=payload, headers=HEADERS_PUBLIC, timeout=15)
        data = _safe_json(r)
        tx_data = data.get("data", {}) or {}
        txstatus = int(tx_data.get("txstatus", 0))
        status_map = {0: "pending", 1: "completed", 2: "failed"}
        status = status_map.get(txstatus, "pending")

        # Let TransactionService handle the wallet effect atomically
        TransactionService.record_transaction(
            user=user,
            amount=_quantize(tx_data.get("amount", 0)),
            transaction_type="deposit",
            reference=reference,
            status=status,
            raw_data=data,
            update_wallet=(status == "completed"),
        )

        logger.info("[MOOLRE][PAYMENT_STATUS] Ref=%s | Status=%s", reference, status)
        return data

    except requests.RequestException as e:
        logger.exception("[MOOLRE][PAYMENT_STATUS] ❌ Error: %s", e)
        return {"status": 0, "message": str(e)}
