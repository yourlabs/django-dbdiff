from dbdiff.tests.decimal_test.models import TestModel as DecimalModel
from dbdiff.tests.nonintpk.models import Nonintpk

import pytest


@pytest.mark.dbdiff(models=[DecimalModel])
def test_insert_first():
    assert DecimalModel.objects.count() == 0
    assert DecimalModel.objects.create(test_field=1).pk == 1


@pytest.mark.dbdiff(models=[DecimalModel])
def test_still_first_pk():
    assert DecimalModel.objects.count() == 0
    assert DecimalModel.objects.create(test_field=1).pk == 1


@pytest.mark.dbdiff(models=[DecimalModel, Nonintpk])
def test_doesnt_reset_nonintpk_which_would_fail():
    assert DecimalModel.objects.count() == 0
