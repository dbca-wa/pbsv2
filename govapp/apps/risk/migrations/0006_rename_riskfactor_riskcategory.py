# Generated by Django 4.2.7 on 2023-11-15 05:43

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        # ("operationalplanning", "0030_operationalplanriskcategory_and_more"),
        (
            "operationalplanning",
            "0029_rename_operationalareariskfactor_operationalplanriskfactor_and_more",
        ),
        ("risk", "0005_standardcontrol"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="RiskFactor",
            new_name="RiskCategory",
        ),
    ]
