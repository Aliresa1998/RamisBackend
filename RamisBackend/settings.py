"""
Django settings for RamisBackend project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-gquaqrf2oj0izp#necaa^y9$d+^wy7z=w!xqu=uo_-53aitgb!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['51.89.247.248', '127.0.0.1', 'localhost']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    ''
    # My Apps
    'rest_framework',
    'drf_spectacular',
    'rest_framework.authtoken',
    'allauth',
    'allauth.account',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'corsheaders',

    # Created Apps
    'users',
    'data',
    'celery',
    'django_celery_beat',
    'azbankgateways',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    'http://51.89.247.248',
    'http://51.89.247.248:8080',
    'http://localhost:3000',
    'http://127.0.0.1:8000',
    'http://51.89.247.248:8089',
    'http://panel.mycryptoprop.com',
    'http://51.89.247.248:8085',
    'http://51.89.247.248:9090',
]
ROOT_URLCONF = 'RamisBackend.urls'

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

WSGI_APPLICATION = 'RamisBackend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ramis',
        'USER': 'admin',
        'PASSWORD': 'admin12345689',
        'HOST': 'localhost',
        'PORT': '',
    }
}
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
FONT_DIR = os.path.join(BASE_DIR, 'static', 'fonts')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]
# jwt config
USE_JWT = True
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'jwt-auth',
    'USER_DETAILS_SERIALIZER': 'users.serializers.UserDetailsSerializer',
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(weeks=999),
    "AUTH_HEADER_TYPES": ("JWT",),
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'ACCOUNT_AUTHENTICATION_METHOD': (
        'username', 'email', 'username_email'
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'PAGE_SIZE': 10,
}

JWT_AUTH_COOKIE = 'my-app-auth'

# Email config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_PORT_SSl = 465
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ramis.req@gmail.com'
EMAIL_HOST_PASSWORD = "ffgedklblwtcwfzg"
SITE_ID = 1
REST_USE_JWT = True
ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
OLD_PASSWORD_FIELD_ENABLED = True
LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
LOGIN_URL = 'http://51.89.247.248:8085/confirm-email'

SPECTACULAR_SETTINGS = {
    'TITLE': 'Ramis project',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',

}
BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
SILENCED_SYSTEM_CHECKS = ['rest_framework.W001']
WKHTMLTOPDF_PATH = os.environ.get('WKHTMLTOPDF_PATH', '/usr/bin/wkhtmltopdf')

# Configure xhtml2pdf
XHTML2PDF = {
    'WKHTMLTOPDF_CMD': WKHTMLTOPDF_PATH,
    'DEFAULT_FONT': 'font.ttf',  # Replace with the font file name
    'DEFAULT_FONT_SIZE': 12,
    'URI_INCLUDES': [],
    'CSS_FILE': os.path.join(BASE_DIR, 'static', 'styles.css'),
}
