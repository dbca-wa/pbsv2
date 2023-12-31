# Generated by Django 4.2.6 on 2023-10-16 03:18

import django.core.validators
from django.db import migrations, models
import model_utils.fields


class Migration(migrations.Migration):
    dependencies = [
        ("burnplanning", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="burnplanunit",
            name="active_from",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(2023)],
            ),
        ),
        migrations.AlterField(
            model_name="burnplanunit",
            name="active_to",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(2023)],
            ),
        ),
        migrations.AlterField(
            model_name="burnplanunit",
            name="status",
            field=model_utils.fields.StatusField(
                choices=[
                    ("draft", "Draft"),
                    ("current", "Current"),
                    ("discarded", "discarded"),
                    ("retired", "Retired"),
                ],
                default="draft",
                max_length=100,
                no_check_for_status=True,
                verbose_name="status",
            ),
        ),
    ]
