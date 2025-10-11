from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import format_html

# Customize the Admin Dashboard Header
admin.site.site_header = "AishWave Admin Dashboard"
admin.site.site_title = "AishWave Admin"
admin.site.index_title = "Welcome to the Dashboard"

# Register the User model with extra info
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

# Create a summary function for the dashboard
def user_summary(request):
    total_users = User.objects.count()
    total_staff = User.objects.filter(is_staff=True).count()
    total_superusers = User.objects.filter(is_superuser=True).count()

    return format_html(
        """
        <div style="background:#f8f9fa; padding:15px; border-radius:10px; margin-bottom:15px;">
            <h2>👥 User Summary</h2>
            <p><b>Total Users:</b> {}<br>
            <b>Admin Staff:</b> {}<br>
            <b>Superusers:</b> {}</p>
        </div>
        """,
        total_users, total_staff, total_superusers
    )

# Add this summary info to the admin homepage
old_each_context = admin.site.each_context
def new_each_context(request):
    context = old_each_context(request)
    context["user_summary"] = user_summary(request)
    return context

admin.site.each_context = new_each_context
