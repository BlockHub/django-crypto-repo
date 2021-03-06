"""
Django settings for crypto_repo project.

Generated by 'django-admin startproject' using Django 2.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from decouple import config, Csv
import raven

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')
STATIC_ROOT = config('STATIC_ROOT')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #third party apps
    'django_extensions',
    'raven.contrib.django.raven_compat',
    'locks',

    # our apps
    'common',
    'bittrex_app',
    'binance_app',
    'bitfinex_app',
    'gdax_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crypto_repo.urls'

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

WSGI_APPLICATION = 'crypto_repo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        }
    }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': config('DEFAULT_DB_NAME'),
            'USER': config('DEFAULT_DB_USER'),
            'PASSWORD': config('DEFAULT_DB_PASSWORD'),
            'HOST': config('DEFAULT_DB_HOST'),
            'PORT': config('DEFAULT_DB_PORT', cast=int),
        },
    }

DATABASE_ROUTERS = [
    'locks.router.Router',
]

LOCKS ={
    'db': 'default'
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_URL = '/static/'

BOTS = {
    'BITTREX': {
        # interval of getting new orderbooks and tickers for all coins (includes time to get info)
        'REFRESH_RATE': config('BITTREX_REFRESH_RATE', cast=int),
        'LOCK_ID': 'BITTREX'
    },
    'BINANCE': {
        # seems it needs to be higher than 60. 120 is working for now
        'REFRESH_RATE': config('BINANCE_REFRESH_RATE', cast=int),
        'LOCK_ID': 'BINANCE'

    },
    'KRAKEN': {
        'REFRESH_RATE': config('KRAKEN_REFRESH_RATE', cast=int),
        'LOCK_ID': 'KRAKEN'

    },
    'BITFINEX': {
        'REFRESH_RATE': config('BITFINEX_REFRESH_RATE', cast=int),
        'LOCK_ID': 'BITFINEX'

    },
    'GDAX': {
        'REFRESH_RATE': config('GDAX_REFRESH_RATE', cast=int),
        'REST_END_POINT': None,
        'WS_ENDPOINT': "wss://ws-feed.gdax.com",
        'LOCK_ID': 'GDAX'

    },
    'HUOBI': {
        'REFRESH_RATE': config('HUOBI_REFRESH_RATE', cast=int),
        'REST_END_POINT': "https://api.huobi.com/",
        'WS_ENDPOINT': None,
        'LOCK_ID': 'HUOBI'

    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'DEBUG',
        'handlers': ['sentry'],
    },

    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': config('SENTRY_HANDLER_LEVEL'),
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': True,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
    },
}

RAVEN_CONFIG = {
    'dsn': config('RAVEN_DSN'),
}