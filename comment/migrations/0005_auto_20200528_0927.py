# Generated by Django 3.0.4 on 2020-05-28 09:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('votarkUser', '0013_auto_20200511_2141'),
        ('comment', '0004_auto_20200520_2352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='votarkUser.VotarkUser'),
        ),
    ]
