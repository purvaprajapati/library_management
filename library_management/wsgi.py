"""
WSGI config for library_management project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')

application = get_wsgi_application()

# Auto-migrate and seed database on server startup
try:
    from django.core.management import call_command
    print("[INIT] Running database migrations...")
    call_command('migrate', interactive=False)

    from accounts.models import UserProfile
    if not UserProfile.objects.exists():
        print("[INIT] Database empty. Seeding initial accounts & books...")
        from seed_data import seed
        seed()
    print("[INIT] Database setup verified.")
except Exception as e:
    print(f"[INIT ERROR] Auto-setup error: {e}", file=sys.stderr)

