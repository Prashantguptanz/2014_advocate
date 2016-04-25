# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Category_Modeler', '0008_addconcepttoalegendoperation_createconceptoperation_createlegendoperation'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassifiedSatelliteImage',
            fields=[
            ],
            options={
                'db_table': 'classified_satellite_image',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SatelliteImage',
            fields=[
            ],
            options={
                'db_table': 'satellite_image',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SetOfOccurences',
            fields=[
            ],
            options={
                'db_table': 'set_of_occurences',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
