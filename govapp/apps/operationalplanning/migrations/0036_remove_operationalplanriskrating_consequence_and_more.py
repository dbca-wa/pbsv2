# Generated by Django 4.2.7 on 2023-11-17 00:48

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("operationalplanning", "0035_operationalplanriskrating"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="operationalplanriskrating",
            name="consequence",
        ),
        migrations.RemoveField(
            model_name="operationalplanriskrating",
            name="likelihood",
        ),
    ]
