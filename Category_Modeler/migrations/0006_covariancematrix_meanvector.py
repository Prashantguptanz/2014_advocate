# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Category_Modeler', '0005_delete_collectingtrainingset'),
    ]

    operations = [
        migrations.CreateModel(
            name='CovarianceMatrix',
            fields=[
            ],
            options={
                'unique_together': set([('covariance_matrix_id', 'matrix_row', 'matrix_column')]),
                'db_table': 'covariance_matrix',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MeanVector',
            fields=[
            ],
            options={
                'db_table': 'mean_vector',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
