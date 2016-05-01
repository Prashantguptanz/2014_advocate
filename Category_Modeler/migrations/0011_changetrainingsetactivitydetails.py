# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Category_Modeler', '0010_auto_20160427_2335'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangeTrainingsetActivityDetails',
            fields=[
            ],
            options={
                'db_table': 'change_trainingset_activity_details',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
