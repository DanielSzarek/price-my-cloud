# Generated by Django 4.1.2 on 2023-03-08 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("node", "0010_alter_component_cpu_utilization"),
    ]

    operations = [
        migrations.AlterField(
            model_name="component",
            name="hidden",
            field=models.BooleanField(default=True),
        ),
    ]