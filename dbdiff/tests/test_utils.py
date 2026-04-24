import os

from django.contrib.auth.models import Group

from dbdiff.utils import diff, get_absolute_path, get_model_names


def test_diff_ignore_pk():
    """With ignore_pk=True, records are matched by content, not pk."""
    expected = {
        'auth.group': {
            1: {'name': 'testgroup', 'permissions': []},
        },
    }
    result = {
        'auth.group': {
            99: {'name': 'testgroup', 'permissions': []},  # diff pk
        },
    }
    unexpected, missing, different = diff(expected, result, ignore_pk=True)
    assert not unexpected and not missing and not different


def test_diff_with_pk_by_default():
    """Records with different pk are missing/unexpected without ignore_pk."""
    expected = {
        'auth.group': {
            1: {'name': 'testgroup', 'permissions': []},
        },
    }
    result = {
        'auth.group': {
            99: {'name': 'testgroup', 'permissions': []},
        },
    }
    unexpected, missing, different = diff(expected, result, ignore_pk=False)
    assert missing == {
        'auth.group': {1: {'name': 'testgroup', 'permissions': []}}
    }
    assert unexpected == {
        'auth.group': {99: {'name': 'testgroup', 'permissions': []}}
    }


def test_get_model_names():
    assert get_model_names([Group, 'auth.user']) == ['auth.group', 'auth.user']


def test_get_absolute_path_starting_with_dot():
    assert get_absolute_path('./foo') == os.path.join(
        os.path.abspath(os.path.dirname('__file__')),
        'foo',
    )
