"""Pytest plugin for django-dbdiff.

The marker enables the smarter sequence reset feature previously available in
the DbdiffTestMixin in pytest, example usage::

    @dbdiff(models=[YourModel])
    def your_test():
        assert YourModel.objects.create().pk == 1
"""
import pytest

from .sequence import sequence_reset


@pytest.fixture(autouse=True)
def _dbdiff_marker(request):
    marker = request.node.get_closest_marker('dbdiff')
    if not marker:
        return

    # Enable transactional db
    request.getfixturevalue('transactional_db')

    for model in marker.kwargs['models']:
        sequence_reset(model)


def pytest_load_initial_conftests(early_config, parser, args):
    """Register the dbdiff mark."""
    early_config.addinivalue_line(
        'markers',
        'dbdiff(models, reset_sequences=True): Mark the test as using '
        'the django test database.  The *transaction* argument marks will '
        "allow you to use real transactions in the test like Django's "
        'TransactionTestCase.')
