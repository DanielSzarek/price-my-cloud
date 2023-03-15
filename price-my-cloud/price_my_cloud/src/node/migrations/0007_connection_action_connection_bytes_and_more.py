# Generated by Django 4.1.2 on 2023-03-06 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("node", "0006_alter_component_options_component_hidden_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="connection",
            name="action",
            field=models.CharField(
                choices=[("ACCEPT", "ACCEPT"), ("REJECT", "REJECT")],
                default=0,
                max_length=64,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="connection",
            name="bytes",
            field=models.PositiveBigIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="connection",
            name="packets",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="connection",
            name="description",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
