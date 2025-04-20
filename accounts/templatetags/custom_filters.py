from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the given value by the arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def subtract(value, arg):
    """Subtract arg from value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value  # Return original value if error
    
@register.filter
def add(value, arg):
    """Add arg from value."""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value  # Return original value if error