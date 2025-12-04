from .base import *

DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']

# Настройки для продакшена
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydatabase',
        'USER': 'mydatabaseuser',
        'PASSWORD': 'mypassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

STATIC_ROOT = BASE_DIR / 'staticfiles'