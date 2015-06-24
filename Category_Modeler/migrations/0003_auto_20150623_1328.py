# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Category_Modeler', '0002_auto_20150525_1901'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Activity',
        ),
        migrations.DeleteModel(
            name='ChangeTrainingSetActivity',
        ),
        migrations.DeleteModel(
            name='Classificationmodel',
        ),
        migrations.DeleteModel(
            name='ClassificationmodelTrainingsets',
        ),
        migrations.DeleteModel(
            name='NewTrainingsetCollectionActivity',
        ),
        migrations.DeleteModel(
            name='TestdataClassificationActivity',
        ),
        migrations.DeleteModel(
            name='TrainClassifierActivity',
        ),
        migrations.CreateModel(
            name='ChangeTrainingset',
            fields=[
            ],
            options={
                'unique_together': set([('newtrainingset_id', 'newtrainingset_ver')]),
                'db_table': 'change_trainingset',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Classification',
            fields=[
            ],
            options={
                'db_table': 'classification',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CollectingTrainingset',
            fields=[
            ],
            options={
                'unique_together': set([('trainingset_id', 'trainingset_ver')]),
                'db_table': 'collecting_trainingset',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Signaturefile',
            fields=[
            ],
            options={
                'db_table': 'signaturefile',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrainClassifier',
            fields=[
            ],
            options={
                'db_table': 'train_classifier',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrainclassifierTrainingsets',
            fields=[
            ],
            options={
                'unique_together': set([('trainingset_id', 'trainingset_ver')]),
                'db_table': 'trainclassifier_trainingsets',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
