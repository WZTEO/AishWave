from .models import LoginHistory
from user_agents import parse
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    parsed_ua = parse(user_agent)

    # Handle cases where device info is unknown
    device = parsed_ua.device.family if parsed_ua.device.family and parsed_ua.device.family != "Other" else "Unknown Device"
    browser = parsed_ua.browser.family if parsed_ua.browser.family else "Unknown Browser"
    os = parsed_ua.os.family if parsed_ua.os.family else "Unknown OS"

    if parsed_ua.is_mobile or parsed_ua.is_tablet:
        device_type = 'Mobile'
    else:
        device_type = 'Laptop/Desktop'

    device_info = f"{device} - {browser} on {os}"

    LoginHistory.objects.create(
        user=user,
        device_info=device_info,
        device_type=device_type
    )
