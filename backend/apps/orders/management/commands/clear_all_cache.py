from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Clear all possible Django caches'

    def handle(self, *args, **options):
        self.stdout.write("🧹 CLEARING ALL CACHES")
        self.stdout.write("=" * 30)
        
        # Clear Django cache
        try:
            cache.clear()
            self.stdout.write(self.style.SUCCESS("✅ Django cache cleared"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error clearing Django cache: {e}"))
        
        # Clear sessions if using database sessions
        try:
            from django.contrib.sessions.models import Session
            Session.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ Database sessions cleared"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️ Could not clear sessions: {e}"))
        
        # Check for Redis cache
        try:
            import redis
            if hasattr(settings, 'CACHES'):
                for cache_name, cache_config in settings.CACHES.items():
                    if 'redis' in cache_config.get('BACKEND', '').lower():
                        self.stdout.write(f"🔍 Found Redis cache: {cache_name}")
                        # You might want to clear Redis here if needed
        except ImportError:
            self.stdout.write("ℹ️ Redis not installed")
        
        # Clear any template cache
        try:
            from django.core.management import call_command
            call_command('collectstatic', '--clear', '--noinput', verbosity=0)
            self.stdout.write(self.style.SUCCESS("✅ Static files cache cleared"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️ Could not clear static files: {e}"))
        
        self.stdout.write(self.style.SUCCESS("\n🎉 Cache clearing complete!"))
        self.stdout.write("💡 Now restart your web server:")
        self.stdout.write("   sudo systemctl restart gunicorn")
        self.stdout.write("   # OR")
        self.stdout.write("   sudo systemctl restart uwsgi")
