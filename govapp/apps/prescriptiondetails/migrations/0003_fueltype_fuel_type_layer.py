# Generated by Django 4.2.7 on 2023-11-29 07:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "prescriptiondetails",
            "0002_burnarea_ffdirange_gfdirange_glcrange_pmcrange_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="fueltype",
            name="fuel_type_layer",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]