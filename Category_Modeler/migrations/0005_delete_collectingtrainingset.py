# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Category_Modeler', '0004_auto_20160224_1600'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CollectingTrainingset',
        ),
    ]
