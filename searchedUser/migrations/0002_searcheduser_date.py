# Generated by Django 3.0.4 on 2020-05-12 20:33

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('searchedUser', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='searcheduser',
            name='date',
            field=models.DateField(default=datetime.datetime(2020, 5, 12, 20, 33, 4, 805550)),
        ),
    ]
