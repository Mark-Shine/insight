# Django 1.5 support, falls back to auth.User to transparently
# work with <1.5
try:
    # from auth.models import User
    from django.contrib.auth.models import User
except ImportError:
    from django.contrib.auth.models import User
