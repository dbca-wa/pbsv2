# Generated by Django 4.2.7 on 2023-11-21 07:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("risk", "0017_additionalcontrol_revisit_in_implementation_plan"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="riskrating",
            unique_together=set(),
        ),
        migrations.AddField(
            model_name="riskrating",
            name="likelihood_of_consequence",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="risk_rating",
                to="risk.likelihoodofconsequence",
            ),
        ),
        migrations.RemoveField(
            model_name="riskrating",
            name="consequence",
        ),
        migrations.RemoveField(
            model_name="riskrating",
            name="likelihood",
        ),
    ]
