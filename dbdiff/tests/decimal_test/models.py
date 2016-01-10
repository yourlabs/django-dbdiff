from django.db import models


class TestModel(models.Model):
    test_field = models.DecimalField(max_digits=5, decimal_places=2)
