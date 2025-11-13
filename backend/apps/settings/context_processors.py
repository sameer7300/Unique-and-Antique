"""
Context processors for template variables.
"""

def admin_theme_context(request):
    """
    Provide theme-related context variables for admin templates.
    """
    return {
        'dark_mode_theme': 'default',
        'card_header': True,
        'is_inline': False,
    }
