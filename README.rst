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
django-representatives and django-representatives-votes which is to be re-used
in django-cities-light.

Database state assertion
========================

A nice way to test a data import script is to create a source data fixture with
a subset of data, ie. with only 10 cities instead of 28K or only 3 european
parliament representatives instead of 3600, feed the import function with that
and then compare the database state with a django fixture. For example:

- use such a command to create a small data extract
  `shuf -n3 cities15000.txt > cities_light/tests/cities_test_fixture.txt`,
- use it against the import script on a clean database,
- verify the database manually, and run
  `django-admin dumpdata --indent=4 cities_light > cities_light/tests/cities_test_expected.txt`
- then, make a test case that calls the import script against the fixture and
  call test_light's function to assert that the database contains only the
  expected data.

When a bug is fixed, just add the case to the fixture and repeat the process to
create new expected data dumps, use coverage to ensure no case is missed.

Predictible serialization
=========================

It is important to use serializers which dump data in a predictible way because
this app relies on diff between an expected - user-generated and versioned -
fixture and dumped database data.

Django's default model-to-dict logic - implemented in
django.core.serializers.python.Serializer.get_dump_object() - returns a dict,
this app registers a slightly modified version of the default json serializer
which returns OrderedDicts instead.

Cross-database fixture compatibility
====================================

MySQL doesn't have microseconds in datetimes, so dbdiff's serializer removes
microseconds from datetimes so that fixtures are cross-database compatible
which make them usable for cross-database testing.

Usage
=====

MySQL, SQLite and PostgreSQL, Python 2.7 and 3.4 are supported along with
Django 1.7 to 1.10 - it's always better to support django's master so that we
can upgrade easily when it is released.

Install ``django-dbdiff`` with pip and add ``dbdiff`` to ``INSTALLED_APPS``.

When ``dbdiff`` is installed, ``dumpdata`` will use its serializers which have
predictible output and cross-database support, so fixtures dumped without
``dbdiff`` installed will have to be regenerated after ``dbdiff`` is installed.

Example::

    from dbdiff import dbdiff

    your_import_function()
    assert not dbdiff.diff('your_app/tests/some_fixture.json')

If any difference is found between the database and the test fixture, then
``diff()`` will return the diff as outputed by GNU diff.

More public API tests can be found in dbidff/tests/test_dbdiff.py.
