from django import template

register = template.Library()

@register.filter
def get_active_investment(investments, user):
    """Returns True if the user has an active investment in the given tier"""
    return any(inv.user == user for inv in investments)