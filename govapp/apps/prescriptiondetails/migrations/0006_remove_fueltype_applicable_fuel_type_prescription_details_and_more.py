# Generated by Django 4.2.7 on 2023-11-30 07:53

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("prescriptiondetails", "0005_applicablefueltypeprescriptiondetail_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="fueltype",
            name="applicable_fuel_type_prescription_details",
        ),
        migrations.DeleteModel(
            name="ApplicableFuelTypePrescriptionDetail",
        ),
    ]
