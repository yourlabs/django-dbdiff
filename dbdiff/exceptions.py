"""Exceptions for dbdiff module."""


class DbDiffException(Exception):
    """Base exception for this app."""


class EmptyFixtures(DbDiffException):
    """Raised when a fixtures file is empty."""

    def __init__(self, path):
        """Exception for when path does not contain any fixture data."""
        super(EmptyFixtures, self).__init__('%s is empty' % path)
