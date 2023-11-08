# Generated by Django 4.2.6 on 2023-11-07 04:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "operationalarea",
            "0008_remove_legalapproval_lga_legalapproval_land_type_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="operationalarea",
            name="mitigation_purpose",
            field=models.CharField(
                blank=True,
                choices=[
                    ("burning", "Burning"),
                    ("mechanical", "Stand-alone Mechanical"),
                ],
                max_length=255,
                null=True,
            ),
        ),
    ]