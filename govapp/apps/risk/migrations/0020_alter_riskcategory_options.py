# Generated by Django 4.2.11 on 2024-03-08 03:52

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("risk", "0019_alter_likelihoodofconsequence_unique_together"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="riskcategory",
            options={
                "verbose_name": "Risk Category",
                "verbose_name_plural": "Risk Categories",
            },
        ),
    ]
