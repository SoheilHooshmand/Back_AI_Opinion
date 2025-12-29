from .base import *

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "77.37.122.76"]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DEVELOPMENT_POSTGRES_DB'),
        'USER': os.getenv('DEVELOPMENT_POSTGRES_USER'),
        'PASSWORD': os.getenv('DEVELOPMENT_POSTGRES_PASSWORD'),
        'HOST': os.getenv('DEVELOPMENT_POSTGRES_HOST', 'db'),
        'PORT': os.getenv('DEVELOPMENT_POSTGRES_PORT', '5432'),
    }
}

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:6789",
    "http://127.0.0.1:6789",
    "http://127.0.0.1:4444",
    "http://localhost:4444",
    "http://127.0.0.1",
    "http://localhost",
    "http://77.37.122.76",
    "http://77.37.122.76:4444",
]
