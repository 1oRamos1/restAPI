from pathlib import Path
from decouple import config
import dj_database_url


# === Base directory ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === Environment detection ===
ENVIRONMENT = config('ENVIRONMENT', default='local')  # 'local' or 'production'
IS_PRODUCTION = ENVIRONMENT == 'production'

# === Security ===
SECRET_KEY = config('SECRET_KEY')
DEBUG = not IS_PRODUCTION

# Allowed hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'tracker-2528.onrender.com']

# === Google OAuth ===
SOCIAL_AUTH_GOOGLE_CLIENT_ID = config('SOCIAL_AUTH_GOOGLE_CLIENT_ID', default='')
SOCIAL_AUTH_GOOGLE_SECRET = config('SOCIAL_AUTH_GOOGLE_SECRET', default='')

# === API Keys ===
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
MISTRAL_API_KEY = config('MISTRAL_API_KEY', default='')
PAYPAL_CLIENT_ID = config('PAYPAL_CLIENT_ID', default='')

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

# === Email backend ===
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' if not IS_PRODUCTION else 'django.core.mail.backends.smtp.EmailBackend'

# === Authentication ===
ACCOUNT_LOGIN_METHODS = {'username'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Redirects
LOGIN_REDIRECT_URL = config('LOGIN_REDIRECT_URL', default='/')
LOGOUT_REDIRECT_URL = config('LOGOUT_REDIRECT_URL', default='/login')
ACCOUNT_LOGOUT_REDIRECT_URL = LOGOUT_REDIRECT_URL

# === Middleware ===
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# === CORS & CSRF ===
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://tracker-2528.onrender.com",
]
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "https://tracker-2528.onrender.com",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = IS_PRODUCTION

CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_NAME = "csrftoken"

# === URLs & templates ===
ROOT_URLCONF = "mysite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [BASE_DIR / "frontend/build"] if IS_PRODUCTION else [],
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

WSGI_APPLICATION = "mysite.wsgi.application"

# === Database ===
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
        ssl_require=IS_PRODUCTION
    )
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
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "frontend/build/static"] if IS_PRODUCTION else []
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'

# === Default PK field ===
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
