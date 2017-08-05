from dbdiff.utils import get_model_names

from django.contrib.auth.models import Group


def test_get_model_names():
    assert get_model_names([Group, 'auth.user']) == ['auth.group', 'auth.user']
