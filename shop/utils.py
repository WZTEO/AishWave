import requests
from django.conf import settings

def create_paystack_recipient(name, account_number, recipient_type, provider_name):
    url = "https://api.paystack.co/transferrecipient"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }
    MOMO_PROVIDERS = {
        "MTN": "mtn",
        "Telecel": "telecel",
        "AirtelTigo": "aiteltigo"
    }
    provider_code = MOMO_PROVIDERS.get(provider_name,"").lower()
    payload = {
        "type": recipient_type, # mobile_money or nuban(bank)
        "name": name,
        "account_number": account_number,
        "bank_code": provider_code,
        "currency": "GHS"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()