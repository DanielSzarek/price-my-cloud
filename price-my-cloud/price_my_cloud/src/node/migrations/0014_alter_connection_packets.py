# Generated by Django 4.1.2 on 2023-03-14 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("node", "0013_component_instance_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="connection",
            name="packets",
            field=models.PositiveBigIntegerField(),
        ),
    ]