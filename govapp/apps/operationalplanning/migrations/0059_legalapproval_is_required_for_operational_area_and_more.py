# Generated by Django 4.2.7 on 2023-12-01 07:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("operationalplanning", "0058_operationalareaapproval"),
    ]

    operations = [
        migrations.AddField(
            model_name="legalapproval",
            name="is_required_for_operational_area",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="legalapproval",
            name="is_required_for_operational_plan",
            field=models.BooleanField(default=False),
        ),
    ]
