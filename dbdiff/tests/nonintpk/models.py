import uuid

from django.db import models


class Nonintpk(models.Model):
    # dbdiff should not try to reset this sequence
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
