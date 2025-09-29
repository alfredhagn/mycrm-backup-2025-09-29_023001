import os
from pathlib import Path

# .env laden
try:
    from dotenv import load_dotenv
    load_dotenv(os.getenv("MYCRM_ENV_FILE", "/etc/mycrm.env"))
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Basis ---
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-unsafe-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in {"1","true","yes","on"}
ALLOWED_HOSTS = ['127.0.0.1','localhost','45.146.253.77','mycrm.interimhagn.de']

# --- Apps ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    "crm_core.apps.CrmCoreConfig",
    "timeclock",
    "ms_tasks",

    # allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.microsoft",
]

SITE_ID = int(os.getenv("SITE_ID", "1"))

# --- Middleware ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    'crm_core.mw_strip59.Strip59Middleware',
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "crm_core.middleware_decimal.DecimalCommaMiddleware",
    'crm_core.middleware.AmountsMiddleware',]

ROOT_URLCONF = "crm_project.urls"
WSGI_APPLICATION = "crm_project.wsgi.application"

# --- Templates ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- DB (MySQL via Unix-Socket) ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "mycrm"),
        "USER": os.getenv("DB_USER", "mycrm"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),  # leer = Unix-Socket
        "PORT": os.getenv("DB_PORT", ""),
        "OPTIONS": {
            "unix_socket": os.getenv("DB_SOCKET", "/run/mysqld/mysqld.sock"),
        },
    }
}

# --- Passwörter ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- i18n / TZ ---
LANGUAGE_CODE = "de"
TIME_ZONE = "Europe/Vienna"
USE_I18N = True
USE_TZ = True

# --- Static/Media ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
_static_local = BASE_DIR / "static"
STATICFILES_DIRS = [_static_local] if _static_local.exists() else []

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- Proxy/HTTPS ---
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "True").lower() in {"1","true","yes","on"}
SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "True").lower() in {"1","true","yes","on"}

# --- Auth / allauth ---
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = "none"

LOGIN_REDIRECT_URL = "/crm/"
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/accounts/login/"

# Tokens & Adapter
SOCIALACCOUNT_STORE_TOKENS = True
SOCIALACCOUNT_ADAPTER = "crm_project.allauth_adapter.PersistTokensAdapter"
# --- MIDDLEWARE (canonical, appended by fix) ---
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "crm_core.middleware_decimal.DecimalCommaMiddleware",
    # Wenn du die OCR-Autofill-Middleware wieder aktivierst:
    # "crm_core.middleware_expense_autofill.ExpenseAutofillMiddleware",  # <- VOR DecimalComma einsortieren
    'crm_core.middleware.AmountsMiddleware',
]
CSRF_TRUSTED_ORIGINS = ['https://mycrm.interimhagn.de']
