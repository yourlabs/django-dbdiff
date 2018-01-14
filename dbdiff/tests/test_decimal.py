import os

from django import test

from .decimal_test.models import TestModel as DecimalTestModel
from ..fixture import Fixture


class DecimalDiffTest(test.TransactionTestCase):
    reset_sequences = True

    expected = os.path.join(
        'dbdiff',
        'tests',
        'decimal_test',
        'expected.json'
    )
    model = DecimalTestModel

    def test_data_diff_is_empty_with_two_decimal_float(self):
        self.model.objects.create(test_field=1.10)
        Fixture(self.expected).assertNoDiff()

    def test_data_diff_is_empty_with_one_decimal_float(self):
        self.model.objects.create(test_field=1.1)
        Fixture(self.expected).assertNoDiff()

    def test_data_diff_is_empty_with_two_decimal_string(self):
        self.model.objects.create(test_field='1.10')
        Fixture(self.expected).assertNoDiff()

    def test_data_diff_is_empty_with_one_decimal_string(self):
        self.model.objects.create(test_field='1.1')
        Fixture(self.expected).assertNoDiff()


class NoReminderDecimalDiffTest(test.TransactionTestCase):
    reset_sequences = True

    expected = os.path.join(
        'dbdiff',
        'tests',
        'decimal_test',
        'expected_no_reminder.json'
    )
    model = DecimalTestModel

    def test_data_diff_is_empty_with_no_decimal_string(self):
        self.model.objects.create(test_field=10)
        Fixture(self.expected).assertNoDiff()

    def test_data_diff_is_empty_with_no_decimal_int(self):
        self.model.objects.create(test_field='10')
        Fixture(self.expected).assertNoDiff()
