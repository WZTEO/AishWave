from django.views.generic import TemplateView

class CustomPasswordResetDoneView(TemplateView):
    template_name = "account/password_reset_done.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = self.request.session.get("password_reset_email", "")
        return context