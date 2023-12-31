# Generated by Django 4.2.7 on 2023-11-15 03:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("operationalplanning", "0027_operationalplan_traffic"),
    ]

    operations = [
        migrations.AlterField(
            model_name="successcriteriareport",
            name="result",
            field=models.CharField(
                blank=True,
                choices=[
                    ("achieved", "Achieved"),
                    ("not_achieved", "Not Achieved"),
                    ("not_started", "Not Started"),
                ],
                max_length=255,
                null=True,
            ),
        ),
    ]
