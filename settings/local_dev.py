"""Local development settings for wger"""

# ruff: noqa: F405
# ruff: noqa: F403

# wger
from .settings_global import *

DEBUG = True

# List of administrators
ADMINS = ['"Your name" <your_email@example.com>']
MANAGERS = ADMINS

# Don't use this key in production!
SECRET_KEY = 'wger-local-development-supersecret-key-1234567890!'

# Allow all hosts to access the application.
ALLOWED_HOSTS = [
    '*',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# WGER application
WGER_SETTINGS['ALLOW_UPLOAD_VIDEOS'] = True
WGER_SETTINGS['ALLOW_GUEST_USERS'] = True
WGER_SETTINGS['ALLOW_REGISTRATION'] = True
WGER_SETTINGS['DOWNLOAD_INGREDIENTS_FROM'] = 'WGER'  # or 'None' to disable
WGER_SETTINGS['EMAIL_FROM'] = 'wger Workout Manager <wger@example.com>'
WGER_SETTINGS['EXERCISE_CACHE_TTL'] = 500
WGER_SETTINGS['INGREDIENT_CACHE_TTL'] = 500
WGER_SETTINGS['SYNC_EXERCISES_CELERY'] = False
WGER_SETTINGS['SYNC_EXERCISE_IMAGES_CELERY'] = True
WGER_SETTINGS['SYNC_EXERCISE_VIDEOS_CELERY'] = False
WGER_SETTINGS['SYNC_INGREDIENTS_CELERY'] = True
WGER_SETTINGS['USE_CELERY'] = False
WGER_SETTINGS['CACHE_API_EXERCISES_CELERY'] = True
WGER_SETTINGS['CACHE_API_EXERCISES_CELERY_FORCE_UPDATE'] = True
WGER_SETTINGS['ROUTINE_CACHE_TTL'] = 500
DEFAULT_FROM_EMAIL = WGER_SETTINGS['EMAIL_FROM']


# CELERY_BROKER_URL = "redis://localhost:6379/2"
# CELERY_RESULT_BACKEND = "redis://localhost:6379/2"

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://192.168.1.131:8000',
    'https://*.trycloudflare.com',
    'https://trifuel.trifuel.workers.dev',
]

# Worker (workers.dev) + named tunnel terminate TLS; honor X-Forwarded-Proto for absolute URLs.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SITE_URL = 'https://trifuel.trifuel.workers.dev'

EXPOSE_PROMETHEUS_METRICS = True

COMPRESS_ENABLED = False
AXES_ENABLED = False


# Does not really cache anything
CACHES_DUMMY = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'TIMEOUT': 100,
    }
}

# In-memory cache, resets when the server restarts
CACHE_LOCMEM = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'wger-cache',
        'TIMEOUT': 100,
    }
}

# Redis cache
CACHE_REDIS = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'TIMEOUT': 5000,
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
    }
}


# CACHES = CACHE_REDIS
CACHES = CACHE_LOCMEM
# CACHES = CACHES_DUMMY


# Django Debug Toolbar
# INSTALLED_APPS += ['django_extensions', 'debug_toolbar']
# MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware", ]
# INTERNAL_IPS = ["127.0.0.1", ]

# AUTH_PROXY_HEADER = 'HTTP_X_REMOTE_USER'
# AUTH_PROXY_USER_EMAIL_HEADER = 'HTTP_X_REMOTE_USER_EMAIL'
# AUTH_PROXY_USER_NAME_HEADER = 'HTTP_X_REMOTE_USER_NAME'
# AUTH_PROXY_TRUSTED_IPS = ['127.0.0.1', ]
# AUTH_PROXY_CREATE_UNKNOWN_USER = True


# Local-only JWT keypair (same as CI fixtures) so Flutter /allauth/app login works.
# Override in local_dev_extra.py for anything shared beyond this Mac.
JWT_PRIVATE_KEY = (
    'eyJhbGciOiAiUlMyNTYiLCAia3R5IjogIlJTQSIsICJuIjogIjlSbXdqZDJadG9DUzg4N0hNY2JpNFpK'
    'RE5WS3dBWG1QSURSby1vejdaWWl1SFpUSzRXNkJYUHpIWnJJd1g5ZXFEOWJBSmNUZzd5NGFKbHRPZ1JY'
    'aFFwdDFZbWo2THRTbkV6NEdRQnM4MjVUS2liS3NIRVpHV2Y5cENWazFleTB3XzNEQTNFSEhQdWNwdEto'
    'cHhzNFFXRERSTEFGamh6WHJVZjQ5X3R2S25aWVcyZ295NEpLVEFsdGFZLUJfemVYYTZZZUx2d1JBbTJU'
    'eVgtV0o5aGVVNjFVRTZ1R2toaTg2Y240WjdlSmsxYmtpNUlxNGRBMC1nVElrNGNzR3VZV2FNU0hfLThP'
    'b1NGU0FjcTFMRGVfdlYwSFhmUHZMMmpSeEhsTkQ1cE12dUlZRU8tNU8yeHVzZU5JU2lJN1YzVDJaWGJG'
    'UWdESHZ2YXlCV0lhQ3V0Z0x5dyIsICJlIjogIkFRQUIiLCAiZCI6ICJJUVFBNEZ0RlpXd1VYM3N2SWVs'
    'a2puWWhUNEZfNl9MdjhLcWVxWUZzSzlVcGZ4cVg2WjMxRncyRjNyT0tDSjhJYlhIRUdGSlk2bDhQYnJO'
    'RjgtVjZubnBLYWFNeWNEUjhfUDZSNFBqS1RkblJIcE5PMDlBemtkUHgxaXlLSTdtR3JDSUlHS05UcjRs'
    'Ny1MWG02YnpBUHVEMGpEVHpyemI0Si1kVGVvMG8wZWt1VnMxTmFHRjBKOUgxeXJyUUt3d1ZtejJEZWoz'
    'OVBERFFWbmVCNk5VNDhzQnRqaFc1YnpBNXF1bWlwSm8tQm9MY0stQ3lBVWl2YVJoYU5IT2U0SDFXYzVT'
    'RlA2czZyeGZ3Z1lNbHlLQVZZU1lvYUVvYThRUTh6akFxN0c3Z3FLQ1dHems5ZkZQUGZjbFVvcGtWWHVJ'
    'elNZdXROV1NDUzQ5eVpJZExENk1JWVEiLCAicCI6ICItb2FHdzNpZElzbVNSNnkxZWNVVlkxYk51QnNG'
    'Q2tFWURWcHNJQjg1YUlJS1NQR1dqTEFjM3hXU1hBZWktekxWY3pQTDVWRVFYQ09Fell2TGV3NWI1MUd0'
    'SXM5MEp5ekxDVGh6SEl4NGlUdnVURUN0U09oMEoxUkxQcDdFbkxKREZsZUItN0txbjFDUWNNREQwV0Vi'
    'SWJZd29XTmNDR1N3dzFEVWZ6RXhfRDAiLCAicSI6ICItblRRY3hHeEdoM3Q2YUluenNSZXhnRkxVaktn'
    'c1NDMUtJMFRqeTRCUktlb040MFhYNXhDSHlfUnRzSkRneUljR1F6UjZNVXZxM0xwTnZNNzRkbHdRUTQ3'
    'YkRCYlJIMjFVc05YeDl0c2phQUpuRGMtX1pONHFyQzNYMFpjM2pRTERuNEUxazFvQWxMTmM0QXNyNVB0'
    'REFUSzF6YzdoaVJqSng4eGdQVjJnS2MiLCAiZHAiOiAiMXpGUzlQalgwUmZnSk56X2pUZHpKYjljT2Za'
    'TG9BRkdEY0pMLWxPWDFtTk5QbGIyZ0thT1JqbWJYSjNhcTNlQXpkSUNKRm83ZVVteE8zWUhOUTZpZHRJ'
    'N3JCa1Nwc3ZkSTNCdndHZ1E2YUNuRXF6RHJFcXY2MUNHeWFWTE1XWVdKa3pJaEZGMktoN2owMVpoWGFy'
    'UnlXVmI1R1VhbXNNUzZ0SzFsUVBHOGVrIiwgImRxIjogImwtaWVQZ3p2QkU0LTdVUWpMUEJDSTRySmFw'
    'TzJqM2l0S0dsWkFiRF9wLXFneHdEV3VuRUdVZkFwSE5aN0tHQlo5bi1tR2E3d0dPZGJ1SzZURll0UzRN'
    'S0hIRG5BUWF5VmZCdHJkSmNNSW1KOU1iajRoY2thbVQwU0c4R0x0bUtPaWoyNUpWcFJ5WWI3Z2lDdC1k'
    'aVpJSDhQb0xXcGJ0VkhKb1Z1LXk3bXIyVSIsICJxaSI6ICJub1QxRnVfMURfUFVxVEY2NlVJWXpNYVZB'
    'bHN5ZU5WMFAydmMycFRZQ1lpb29lam4xNkEwc3FMMHZ3VmstM2Mzc2dtU0oyejc4SklWTXoxMlFtTHl1'
    'aGlMa01HZEpzeUJUYTdnWGI2RXcxQnFHTmxoVHFXX0p6RGJEclNmSEJpMnA5dFZPUFVTSW5ZaURxbXRy'
    'bkFMWnVDZ3ZqUFItVzlPaF9rTUlNbUJQUmMiLCAia2lkIjogImNpLXRlc3QifQ=='
)
JWT_PUBLIC_KEY = (
    'eyJrdHkiOiAiUlNBIiwgIm4iOiAiOVJtd2pkMlp0b0NTODg3SE1jYmk0WkpETlZLd0FYbVBJRFJvLW96'
    'N1pZaXVIWlRLNFc2QlhQekhackl3WDllcUQ5YkFKY1RnN3k0YUpsdE9nUlhoUXB0MVltajZMdFNuRXo0'
    'R1FCczgyNVRLaWJLc0hFWkdXZjlwQ1ZrMWV5MHdfM0RBM0VISFB1Y3B0S2hweHM0UVdERFJMQUZqaHpY'
    'clVmNDlfdHZLblpZVzJnb3k0SktUQWx0YVktQl96ZVhhNlllTHZ3UkFtMlR5WC1XSjloZVU2MVVFNnVH'
    'a2hpODZjbjRaN2VKazFia2k1SXE0ZEEwLWdUSWs0Y3NHdVlXYU1TSF8tOE9vU0ZTQWNxMUxEZV92VjBI'
    'WGZQdkwyalJ4SGxORDVwTXZ1SVlFTy01TzJ4dXNlTklTaUk3VjNUMlpYYkZRZ0RIdnZheUJXSWFDdXRn'
    'THl3IiwgImUiOiAiQVFBQiIsICJhbGciOiAiUlMyNTYiLCAia2lkIjogImNpLXRlc3QifQ=='
)
_jwt_private_pem = jwk_b64_to_pem(JWT_PRIVATE_KEY)
_jwt_public_pem = jwk_b64_to_pem(JWT_PUBLIC_KEY)
SIMPLE_JWT['SIGNING_KEY'] = _jwt_private_pem
SIMPLE_JWT['VERIFYING_KEY'] = _jwt_public_pem
SIMPLE_JWT['ALGORITHM'] = 'RS256'
HEADLESS_JWT_PRIVATE_KEY = _jwt_private_pem

DBCONFIG_PG = {
    'ENGINE': 'django_prometheus.db.backends.postgresql',
    'NAME': 'wger',
    'USER': 'wger',
    'PASSWORD': 'wger',
    'HOST': 'localhost',
    'PORT': '5432',
}


DBCONFIG_SQLITE = {
    'ENGINE': 'django_prometheus.db.backends.sqlite3',
    'NAME': BASE_DIR.parent / 'db' / 'database.sqlite',
}

DATABASES = {
    'default': DBCONFIG_PG,
    # 'default': DBCONFIG_SQLITE,
}


# Import other local settings that are not in version control
try:
    from .local_dev_extra import *
except ImportError:
    pass
