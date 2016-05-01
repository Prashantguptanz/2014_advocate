# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Category_Modeler', '0009_classifiedsatelliteimage_satelliteimage_setofoccurences'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TrainingsetCollectionActivity',
        ),
        migrations.CreateModel(
            name='CreateTrainingsetActivity',
            fields=[
            ],
            options={
                'unique_together': set([('trainingsample_for_category1_id', 'trainingsample_for_category1_ver')]),
                'db_table': 'create_trainingset_activity',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrainingsampleCollection',
            fields=[
            ],
            options={
                'unique_together': set([('trainingsample_id', 'trainingsample_ver')]),
                'db_table': 'trainingsample_collection',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrainingsampleForCategory',
            fields=[
            ],
            options={
                'db_table': 'trainingsample_for_category',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrainingsetTrainingsamples',
            fields=[
            ],
            options={
                'unique_together': set([('trainingsample_id', 'trainingsample_ver')]),
                'db_table': 'trainingset_trainingsamples',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
