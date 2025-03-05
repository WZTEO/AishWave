from django.shortcuts import redirect
from django.urls import reverse

class PasswordResetMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        login_url = reverse("account_login")

        # Avoid infinite redirect loops
        if request.path == login_url or request.method == "POST":
            return self.get_response(request)

        # Redirect password reset info pages to login
        if request.path.startswith("/accounts/password/reset/done/") or request.path.startswith("/accounts/password/reset/key/done/"):
            return redirect(login_url)

        return self.get_response(request)