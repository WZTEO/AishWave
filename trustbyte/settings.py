"""
Django settings for trustbyte project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(',')

PAYSTACK_CALLBACK = os.getenv("PAYSTACK_CALLBACK")
# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'authentication',
    'shop',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.apple',
    'allauth.socialaccount.providers.facebook',
    'widget_tweaks',
    
]

JAZZMIN_SETTINGS = {
    "site_title": "AishWave",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "AishWave",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "AishWave",

    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": "trustbyte/img/logo.jpg",

    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": None,

    # Logo to use for login form in dark themes (defaults to login_logo)
    "login_logo_dark": None,

    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",
    "related_modal_active": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "account.Emailaddress": "fas fa-envelope",
        "shop.Transaction": "fas fa-money-bill-transfer",
        "shop.Wallet": "fas fa-wallet",
        "shop.Order": "fas fa-cube",
        "shop.Referral": "fas fa-share",
        "shop.Discount": "fas fa-percent",
        "shop.WithdrawalRequest": "fas fa-sack-dollar",
        "shop.Investment": "fas fa-hand-holding-dollar",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
#    "show_ui_builder": True,  # Enable UI Customizer
}
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-info",
    "accent": "accent-primary",
    "navbar": "navbar-cyan navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-light-info",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "yeti",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
]
PAYSTACK_PUBLIC_KEY = "pk_test_206c2bfe4b2bb70a9c846d739044f68ec5bbbfb4"
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',

]


SOCIALACCOUNT_LOGIN_ON_GET= True
SOCIALACCOUNT_AUTO_SIGNUP= True

SITE_ID = 1
SOCIALACCOUNT_QUERY_EMAIL = True  # Force allauth to request email
SOCIALACCOUNT_STORE_TOKENS = True  # Store authentication tokens
SOCIALACCOUNT_ADAPTER = "authentication.adapters.MySocialAccountAdapter"

ACCOUNT_LOGIN_METHODS = {'email'}
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT=True
ACCOUNT_EMAIL_REQUIRED = True  # Ensure email is required
ACCOUNT_USERNAME_REQUIRED = False  # Ensure username is required
ACCOUNT_SIGNUP_REDIRECT_URL = '/dashboard'  # Prevent immediate redirectACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_FORMS = {
    'signup': 'authentication.forms.CustomSignupForm',
}
SOCIALACCOUNT_LOGOUT_ON_GET = False  # Logs out immediately when visiting the logout URL
LOGIN_REDIRECT_URL = "/dashboard"  # Change this as needed
LOGOUT_REDIRECT_URL = "/accounts/login"

ROOT_URLCONF = 'trustbyte.urls'

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")  # Change based on your provider
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")  # Replace with your email
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")  # Use an environment variable for security
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'trustbyte.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CSRF_TRUSTED_ORIGINS = ["https://quetzal-keen-infinitely.ngrok-free.app"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # Optional: Only if you have a global static folder
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Used for production (optional)

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
