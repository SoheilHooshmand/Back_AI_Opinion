from .base import *

DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
CSRF_TRUSTED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PRODUCTION_POSTGRES_DB'),
        'USER': os.getenv('PRODUCTION_POSTGRES_USER'),
        'PASSWORD': os.getenv('PRODUCTION_POSTGRES_PASSWORD'),
        'HOST': os.getenv('PRODUCTION_POSTGRES_HOST', 'db'),
        'PORT': os.getenv('PRODUCTION_POSTGRES_PORT', '5432'),
    }
}

