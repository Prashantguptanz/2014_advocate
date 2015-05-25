# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Category_Modeler', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ClassificationmodelTrianingsets',
        ),
        migrations.CreateModel(
            name='ClassificationmodelTrainingsets',
            fields=[
            ],
            options={
                'db_table': 'classificationmodel_trainingsets',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
