# Generated by Django 3.0.4 on 2020-05-21 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0013_remove_post_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='video',
            field=models.FileField(null=True, upload_to='videos/', verbose_name=''),
        ),
    ]
