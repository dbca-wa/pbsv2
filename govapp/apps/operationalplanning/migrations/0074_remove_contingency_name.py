# Generated by Django 4.2.7 on 2023-12-12 03:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "operationalplanning",
            "0073_rename_disturbance_approval_operationalarea_disturbance_application_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="contingency",
            name="name",
        ),
    ]
