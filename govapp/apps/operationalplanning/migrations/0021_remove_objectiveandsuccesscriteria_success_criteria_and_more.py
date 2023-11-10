# Generated by Django 4.2.6 on 2023-11-09 08:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        (
            "operationalplanning",
            "0020_objective_successcriteriacomparisonoperator_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="objectiveandsuccesscriteria",
            name="success_criteria",
        ),
        migrations.AddField(
            model_name="successcriteria",
            name="objective_and_success_criteria",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="success_criterias",
                to="operationalplanning.objectiveandsuccesscriteria",
            ),
        ),
    ]