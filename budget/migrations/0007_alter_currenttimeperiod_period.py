# Generated by Django 5.0.6 on 2024-05-23 23:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0006_currenttimeperiod'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currenttimeperiod',
            name='period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budget.timeperiod'),
        ),
    ]
