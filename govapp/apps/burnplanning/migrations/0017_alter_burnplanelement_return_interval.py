# Generated by Django 4.2.9 on 2024-02-06 04:10

import django.core.validators
from django.db import migrations
import govapp.apps.main.models


class Migration(migrations.Migration):
    dependencies = [
        ("burnplanning", "0016_alter_burnplanunit_return_interval"),
    ]

    operations = [
        migrations.AlterField(
            model_name="burnplanelement",
            name="return_interval",
            field=govapp.apps.main.models.IntervalIntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(1)],
            ),
        ),
    ]
