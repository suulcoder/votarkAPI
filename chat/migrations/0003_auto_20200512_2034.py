# Generated by Django 3.0.4 on 2020-05-12 20:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_chat_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]