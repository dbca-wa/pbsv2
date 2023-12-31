# Generated by Django 4.2.6 on 2023-11-01 04:30

from django.db import migrations, models
import django.db.models.deletion
import govapp.apps.main.models
import protected_media.models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0010_lga"),
        ("operationalplanning", "0003_alter_operationalareaapproval_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="operationalareaapproval",
            options={"verbose_name_plural": "Operational Area Legal/Approvals"},
        ),
        migrations.RemoveField(
            model_name="operationalarea",
            name="approvals",
        ),
        migrations.AddField(
            model_name="operationalareaapproval",
            name="operational_area",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="operationalareaapprovals",
                to="operationalplanning.operationalarea",
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="LegalApproval",
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
                (
                    "display_name",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("approver", models.CharField(blank=True, max_length=255, null=True)),
                ("can_provide_evidence", models.BooleanField(default=False)),
                (
                    "file_as_approval",
                    protected_media.models.ProtectedFileField(
                        storage=protected_media.models.ProtectedFileSystemStorage(),
                        upload_to=govapp.apps.main.models.file_upload_location,
                    ),
                ),
                ("text_as_approval", models.TextField(blank=True, null=True)),
                ("text_remove_justification", models.TextField(blank=True, null=True)),
                (
                    "lga",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="main.lga",
                    ),
                ),
            ],
            options={
                "verbose_name": "Operational Area Legal/Approval",
                "verbose_name_plural": "Operational Area Legal/Approvals",
            },
        ),
        migrations.AddField(
            model_name="operationalarea",
            name="legal_approvals",
            field=models.ManyToManyField(
                editable=False,
                related_name="operational_areas",
                through="operationalplanning.OperationalAreaApproval",
                to="operationalplanning.legalapproval",
            ),
        ),
        migrations.AddField(
            model_name="operationalareaapproval",
            name="legal_approval",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="operationalareaapprovals",
                to="operationalplanning.legalapproval",
            ),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name="operationalareaapproval",
            unique_together={("operational_area", "legal_approval")},
        ),
        migrations.RemoveField(
            model_name="operationalareaapproval",
            name="approver",
        ),
        migrations.RemoveField(
            model_name="operationalareaapproval",
            name="can_provide_evidence",
        ),
        migrations.RemoveField(
            model_name="operationalareaapproval",
            name="file_as_approval",
        ),
        migrations.RemoveField(
            model_name="operationalareaapproval",
            name="lga",
        ),
        migrations.RemoveField(
            model_name="operationalareaapproval",
            name="text_as_approval",
        ),
        migrations.RemoveField(
            model_name="operationalareaapproval",
            name="text_remove_justification",
        ),
    ]
