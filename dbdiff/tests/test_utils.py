import os

from dbdiff.utils import get_absolute_path, get_model_names

from django.contrib.auth.models import Group


def test_get_model_names():
    assert get_model_names([Group, 'auth.user']) == ['auth.group', 'auth.user']


def test_get_absolute_path_starting_with_dot():
    assert get_absolute_path('./foo') == os.path.join(
        os.path.abspath(os.path.dirname('__file__')),
        'foo',
    )
