# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Category_Modeler', '0006_covariancematrix_meanvector'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeEvent',
            fields=[
            ],
            options={
                'db_table': 'change_event',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChangeEventOperations',
            fields=[
            ],
            options={
                'db_table': 'change_event_operations',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
