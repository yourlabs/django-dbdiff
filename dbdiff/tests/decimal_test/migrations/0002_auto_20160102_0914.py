# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('decimal_test', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testmodel',
            name='test_field',
            field=models.DecimalField(max_digits=5, decimal_places=2),
        ),
    ]
