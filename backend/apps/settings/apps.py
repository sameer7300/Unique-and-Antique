"""
Configuration for the settings app.
"""

from django.apps import AppConfig


class SettingsConfig(AppConfig):
    """
    Configuration for the settings app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.settings'
    verbose_name = 'Site Settings'
