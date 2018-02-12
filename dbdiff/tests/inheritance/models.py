from django.db import models


class Parent(models.Model):
    pass


class Child(Parent):
    name = models.CharField(max_length=50)
