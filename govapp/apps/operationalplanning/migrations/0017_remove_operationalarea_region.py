# Generated by Django 4.2.6 on 2023-11-09 03:23

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "operationalplanning",
            "0016_remove_operationalarea_mitigation_purpose_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="operationalarea",
            name="region",
        ),
    ]
