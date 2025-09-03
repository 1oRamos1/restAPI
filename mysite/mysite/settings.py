from pathlib import Path
from decouple import config


# === Security ===
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# === Google OAuth ===
SOCIAL_AUTH_GOOGLE_CLIENT_ID = config('SOCIAL_AUTH_GOOGLE_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_SECRET = config('SOCIAL_AUTH_GOOGLE_SECRET')

# === OpenAI ===
OPENAI_API_KEY = config('OPENAI_API_KEY')

# === Paypal ===
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID')

BASE_DIR = Path(__file__).resolve().parent.parent
ALLOWED_HOSTS = ['tracker-production-387a.up.railway.app', 'localhost', '127.0.0.1']

REST_USE_JWT = False
# === Installed apps ===
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django_extensions",

    "tracker",

    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",

    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    "dj_rest_auth",
    "dj_rest_auth.registration",
]

SITE_ID = 1

# === Email (console) ===
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# === Authentication settings ===
ACCOUNT_LOGIN_METHODS = {'username'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_LOGIN_ON_GET = True

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

ACCOUNT_LOGOUT_REDIRECT_URL = 'http://localhost:3000/login'
LOGIN_REDIRECT_URL = 'http://localhost:3000/'
LOGOUT_REDIRECT_URL = 'http://localhost:3000/'

# === Google OAuth ===
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': config('SOCIAL_AUTH_GOOGLE_CLIENT_ID'),
            'secret': config('SOCIAL_AUTH_GOOGLE_SECRET'),
            'key': ''
        },
    }
}

# === Middleware ===
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# === CORS & CSRF ===
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "https://tracker-production-387a.up.railway.app",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS

CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_NAME = "csrftoken"

# === URLs ===
ROOT_URLCONF = "mysite.urls"

# === Templates ===
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "frontend/build"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# === WSGI ===
WSGI_APPLICATION = "mysite.wsgi.application"

# === Database ===
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# === Password validators ===
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# === DRF ===
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'tracker.serializers.CustomUserDetailsSerializer',
}

# === Locale ===
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# === Static files ===
STATIC_URL = "static/"

# === Default PK field ===
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATICFILES_DIRS = [
    BASE_DIR / 'frontend/build/static',

]
STATIC_ROOT = BASE_DIR / 'staticfiles'