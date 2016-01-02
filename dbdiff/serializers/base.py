"""Shared code for serializers."""

import collections
import datetime
import decimal


class BaseSerializerMixin(object):
    """Serializer mixin for predictible and cross-db dumps."""

    @classmethod
    def recursive_dict_sort(cls, data):
        """Return a recursive OrderedDict for a dict."""
        ordered_data = collections.OrderedDict(sorted(data.items()))

        for key, value in ordered_data.items():
            if isinstance(value, dict):
                ordered_data[key] = cls.recursive_dict_sort(value)

        return ordered_data

    @classmethod
    def remove_microseconds(cls, data):
        """Strip microseconds from datetimes for mysql."""
        for key, value in data['fields'].items():
            if not isinstance(value, datetime.datetime):
                continue

            data['fields'][key] = datetime.datetime(
                year=value.year,
                month=value.month,
                day=value.day,
                hour=value.hour,
                minute=value.minute,
                second=value.second,
                tzinfo=value.tzinfo
            )

    @classmethod
    def normalize_decimals(cls, data):
        """Strip trailing zeros for constitency."""
        for key, value in data['fields'].items():
            if not isinstance(value, decimal.Decimal):
                continue

            data['fields'][key] = value.normalize()

    def get_dump_object(self, obj):
        """Actual method used by Django serializers to dump dicts."""
        data = super(BaseSerializerMixin, self).get_dump_object(obj)
        self.remove_microseconds(data)
        self.normalize_decimals(data)
        data = self.recursive_dict_sort(data)
        return data
