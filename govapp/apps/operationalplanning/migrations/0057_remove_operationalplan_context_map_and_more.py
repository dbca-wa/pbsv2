# Generated by Django 4.2.7 on 2023-12-01 02:56

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("operationalplanning", "0056_alter_prescriptionfueltype_glc_range_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="operationalplan",
            name="context_map",
        ),
        migrations.RemoveField(
            model_name="operationalplanapproval",
            name="file_as_approval",
        ),
    ]
