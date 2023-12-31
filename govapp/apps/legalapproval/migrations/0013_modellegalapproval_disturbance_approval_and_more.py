# Generated by Django 4.2.7 on 2023-12-11 04:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("legalapproval", "0012_remove_otherapproval_created_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="modellegalapproval",
            name="disturbance_approval",
            field=models.ManyToManyField(
                related_name="modellegalapproval_das_approvals",
                to="legalapproval.disturbanceapplication",
            ),
        ),
        migrations.AddField(
            model_name="modellegalapproval",
            name="fauna_authority_to_take",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="modellegalapproval_fauna_atts",
                to="legalapproval.authoritytotake",
            ),
        ),
        migrations.AddField(
            model_name="modellegalapproval",
            name="flora_authority_to_take",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="modellegalapproval_flora_atts",
                to="legalapproval.authoritytotake",
            ),
        ),
    ]
