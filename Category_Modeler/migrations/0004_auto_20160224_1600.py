# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Category_Modeler', '0003_auto_20150623_1328'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ChangeTrainingset',
        ),
        migrations.DeleteModel(
            name='Classification',
        ),
        migrations.DeleteModel(
            name='Relationship',
        ),
        migrations.DeleteModel(
            name='Signaturefile',
        ),
        migrations.DeleteModel(
            name='TrainClassifier',
        ),
        migrations.DeleteModel(
            name='TrainclassifierTrainingsets',
        ),
        migrations.CreateModel(
            name='ChangeTrainingsetActivity',
            fields=[
            ],
            options={
                'unique_together': set([('newtrainingset_id', 'newtrainingset_ver')]),
                'db_table': 'change_trainingset_activity',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClassificationActivity',
            fields=[
            ],
            options={
                'db_table': 'classification_activity',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Classificationmodel',
            fields=[
            ],
            options={
                'db_table': 'classificationmodel',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComputationalIntension',
            fields=[
            ],
            options={
                'db_table': 'computational_intension',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Confusionmatrix',
            fields=[
            ],
            options={
                'db_table': 'confusionmatrix',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Extension',
            fields=[
            ],
            options={
                'db_table': 'extension',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HierarchicalRelationship',
            fields=[
            ],
            options={
                'db_table': 'hierarchical_relationship',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HorizontalRelationship',
            fields=[
            ],
            options={
                'unique_together': set([('category2_id', 'category2_ver')]),
                'db_table': 'horizontal_relationship',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LearningActivity',
            fields=[
            ],
            options={
                'db_table': 'learning_activity',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LegendConceptCombination',
            fields=[
            ],
            options={
                'unique_together': set([('legend_id', 'legend_ver')]),
                'db_table': 'legend_concept_combination',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrainingsetCollectionActivity',
            fields=[
            ],
            options={
                'unique_together': set([('trainingset_id', 'trainingset_ver')]),
                'db_table': 'trainingset_collection_activity',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
