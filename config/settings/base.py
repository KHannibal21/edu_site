from pathlib import Path

# Корень проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = 'django-insecure-your-secret-key-here'

DEBUG = True
ALLOWED_HOSTS = []

# Приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',  # ← ИСПРАВЛЕНО: auth вместо accounts
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Приложения проекта
    'apps.home',
    'apps.about',
    'apps.quizzes',
    'apps.courses',
    'apps.users',
    'apps.analytics',
    'apps.events',
    'apps.accounts',  # ← Это ваше приложение, оставляем
]

# Мидлвары
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # ← ИСПРАВЛЕНО: auth вместо accounts
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# Шаблоны
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',  # ← ИСПРАВЛЕНО: auth вместо accounts
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# База данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Статика
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Аутентификация
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# URL для перенаправления после входа/выхода
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/auth/login/'