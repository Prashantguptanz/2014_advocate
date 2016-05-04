# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Category_Modeler', '0011_changetrainingsetactivitydetails'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AddConceptToALegendOperation',
        ),
        migrations.DeleteModel(
            name='CreateConceptOperation',
        ),
        migrations.DeleteModel(
            name='CreateLegendOperation',
        ),
        migrations.CreateModel(
            name='AddConceptOperation',
            fields=[
            ],
            options={
                'db_table': 'Add_Concept_operation',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AddTaxonomyOperation',
            fields=[
            ],
            options={
                'unique_together': set([('legend_id', 'legend_ver')]),
                'db_table': 'Add_Taxonomy_operation',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CategoryInstantiationOperation',
            fields=[
            ],
            options={
                'unique_together': set([('category_id', 'category_evol_ver', 'category_comp_ver')]),
                'db_table': 'Category_Instantiation_operation',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CreateTrainingsetActivityOperations',
            fields=[
            ],
            options={
                'db_table': 'create_trainingset_activity_operations',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
