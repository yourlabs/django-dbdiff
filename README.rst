.. image:: https://travis-ci.org/yourlabs/django-dbdiff.svg
    :target: https://travis-ci.org/yourlabs/django-dbdiff
.. image:: https://codecov.io/github/yourlabs/django-dbdiff/coverage.svg?branch=master
    :target: https://codecov.io/github/yourlabs/django-dbdiff?branch=master
.. image:: https://badge.fury.io/py/django-dbdiff.png
   :target: http://badge.fury.io/py/django-dbdiff

django-dbdiff
~~~~~~~~~~~~~

I'm pretty lazy when it comes to writing tests for existing code, however, I'm
even lazier when it comes to repetitive manual testing action.

This package aims at de-duplicating the data import tests from
django-representatives and django-representatives-votes which is re-used in
django-cities-light.

Database state assertion
========================

A nice way to test a data import script is to create a source data fixture with
a subset of data, ie. with only 10 cities instead of 28K or only 3 european
parliament representatives instead of 3600, feed the import function with that
and then compare the database state with a django fixture. This looks like what
I was used to do:

- use such a command to create a small data extract
  `shuf -n3 cities15000.txt > cities_light/tests/cities_test_fixture.txt`,
- use it against the import script on a clean database,
- verify the database manually, and run
  `django-admin dumpdata --indent=4 cities_light > cities_light/tests/cities_test_expected.txt`
- then, make a test case that calls the import script against the fixture,
- write and maintain some funny (fuzzy ?) repetitive test code to ensure that
  the database is in the expected state.

When a bug is fixed, just add the case to the fixture and repeat the process to
create new expected data dumps, use coverage to ensure no case is missed.

With django-dbdiff, I just need to maintain to initial data extract, and test
it with ``Fixture('appname/path/to/fixture',
models=[YourModelToTest]).assertNoDiff()`` in a
``django.test.TransactionTestCase`` which has ``reset_sequences=True``:

- if the fixture in question doesn't exist, it'll be automatically created on
  with dumpdata for the concerned models on the first run, raising
  "FixtureCreated" exception to fail the test and inform of the path of the
  created fixture, so that it doesn't mislead the user in thinking the test
  passed with an existing fixture,
- if the fixture exists, it'll run dumpdata on the models concerned and GNU
  diff it against the fixture, if there's any output it'll be raised in the
  "DiffFound" exception, failing the test and printing the diff.

Usage
=====

Example::

    from django import TransactionTestCase
    from dbdiff.fixture import Fixture


    class YourImportTest(test.TransactionTestCase):
        reset_sequences = True

        def test_your_import(self):
            your_import()

            Fixture('yourapp/tests/yourtest.json',
                    models=[YourModel]).assertNoDiff()

The first time, it will raise a ``FixtureCreated`` exception, and the test will
fail. This is to inform the user that the test didn't really run. On the next
run though, it will pass.

If any difference is found between the database and the test fixture, then
``diff()`` will return the diff as outputed by GNU diff.

See tests and docstrings for crunchy details.

Requirements
============

MySQL, SQLite and PostgreSQL, Python 2.7 and 3.4 are supported along with
Django 1.7 to 1.10 - it's always better to support django's master so that we
can **upgrade easily when it is released**, which is one of the selling points
for having 100% coverage.

Install
=======

Install ``django-dbdiff`` with pip and add ``dbdiff`` to ``INSTALLED_APPS``.

Django model observer
=====================

It is interresting to note that a related, perhaps sort-of similar app exists:
https://github.com/Griffosx/djmo
