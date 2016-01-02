from .settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dbdiff_test',
        'USER': 'postgres',
    }
}
