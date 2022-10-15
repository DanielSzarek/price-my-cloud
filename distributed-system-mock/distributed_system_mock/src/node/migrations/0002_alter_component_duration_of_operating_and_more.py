# Generated by Django 4.1.2 on 2022-10-15 19:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("node", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="component",
            name="duration_of_operating",
            field=models.DurationField(default=datetime.timedelta(microseconds=100000)),
        ),
        migrations.AlterField(
            model_name="connection",
            name="avg_time_of_request",
            field=models.DurationField(default=datetime.timedelta(microseconds=100000)),
        ),
    ]
