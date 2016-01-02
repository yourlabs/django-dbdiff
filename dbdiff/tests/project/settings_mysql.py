from .settings import *  # noqa

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dbdiff_test',
        'USER': 'root',
    }
}
