# Generated by Django 4.1.2 on 2023-03-14 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aws", "0003_rename_packet_flowlogdata_packets"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flowlogdata",
            name="bytes",
            field=models.PositiveBigIntegerField(),
        ),
        migrations.AlterField(
            model_name="flowlogdata",
            name="packets",
            field=models.PositiveBigIntegerField(),
        ),
    ]