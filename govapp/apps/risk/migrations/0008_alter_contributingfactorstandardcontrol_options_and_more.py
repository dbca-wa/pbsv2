# Generated by Django 4.2.7 on 2023-11-16 03:17

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):
    dependencies = [
        ("risk", "0007_contributingfactorstandardcontrol_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="contributingfactorstandardcontrol",
            options={
                "verbose_name": "Standard Control Default Value",
                "verbose_name_plural": "Standard Control Default Values",
            },
        ),
        migrations.AlterUniqueTogether(
            name="contributingfactorstandardcontrol",
            unique_together={("contributing_factor", "standard_control")},
        ),
        migrations.CreateModel(
            name="OverwriteControl",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "standard_control",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="overwrite_controls",
                        to="risk.standardcontrol",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
