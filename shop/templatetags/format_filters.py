from django import template

register = template.Library()

@register.filter
def pretty_name(value: str) -> str:
    """
    Converts snake_case or underscore_separated text into Title Case with spaces.
    Example:
        'data_purchase' → 'Data Purchase'
        'task_reward'   → 'Task Reward'
    """
    if not value:
        return ""
    return str(value).replace("_", " ").title()
