# Generated by Django 4.2.6 on 2023-10-31 04:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("risk", "0003_alter_contributingfactor_factors"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="riskfactor",
            name="contributing_factor",
        ),
        migrations.RemoveField(
            model_name="riskfactor",
            name="values_affected",
        ),
    ]
