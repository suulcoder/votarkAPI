# Generated by Django 3.0.4 on 2020-05-23 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0014_post_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='victories',
            field=models.IntegerField(default=0),
        ),
    ]
