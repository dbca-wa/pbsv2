# Generated by Django 4.2.7 on 2023-11-21 01:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("risk", "0016_contributingfactorstandardcontrol_created_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="additionalcontrol",
            name="revisit_in_implementation_plan",
            field=models.BooleanField(default=False),
        ),
    ]
