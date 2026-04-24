import os
import sys
import django

sys.path.insert(0, os.path.abspath('..'))
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'dbdiff.tests.project.settings_sqlite',
)
django.setup()

project = 'django-dbdiff'
copyright = '2026, James Pic'
author = 'James Pic'
release = '0.9.7'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

html_theme = 'alabaster'
