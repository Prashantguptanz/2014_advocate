# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Category_Modeler', '0007_changeevent_changeeventoperations'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddConceptToALegendOperation',
            fields=[
            ],
            options={
                'unique_together': set([('category_id', 'category_ver')]),
                'db_table': 'add_concept_to_a_legend_operation',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CreateConceptOperation',
            fields=[
            ],
            options={
                'db_table': 'create_concept_operation',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CreateLegendOperation',
            fields=[
            ],
            options={
                'unique_together': set([('legend_id', 'legend_ver')]),
                'db_table': 'create_legend_operation',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
