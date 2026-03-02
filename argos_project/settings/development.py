from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Local SQLite for dev
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
