# Generated by Django 3.0.4 on 2020-05-14 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0005_auto_20200513_0916'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='content',
        ),
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='post',
            name='video',
            field=models.FileField(null=True, upload_to='videos/', verbose_name=''),
        ),
    ]