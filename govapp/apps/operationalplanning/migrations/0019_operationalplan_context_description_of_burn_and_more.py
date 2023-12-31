# Generated by Django 4.2.6 on 2023-11-09 04:29

from django.db import migrations, models
import govapp.apps.main.models
import protected_media.models


class Migration(migrations.Migration):
    dependencies = [
        ("operationalplanning", "0018_operationalplan_window_of_opportunity_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="operationalplan",
            name="context_description_of_burn",
            field=models.TextField(
                blank=True, null=True, verbose_name="Description of burn"
            ),
        ),
        migrations.AddField(
            model_name="operationalplan",
            name="context_map",
            field=protected_media.models.ProtectedFileField(
                blank=True,
                null=True,
                storage=protected_media.models.ProtectedFileSystemStorage(),
                upload_to=govapp.apps.main.models.file_upload_location,
            ),
        ),
        migrations.AddField(
            model_name="operationalplan",
            name="context_operational_aspects",
            field=models.TextField(
                blank=True, null=True, verbose_name="Operational aspects (PESTLE)"
            ),
        ),
        migrations.AddField(
            model_name="operationalplan",
            name="context_risk_of_not_completing_burn",
            field=models.TextField(
                blank=True, null=True, verbose_name="Risk of not completing burn"
            ),
        ),
    ]
