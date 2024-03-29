# Generated by Django 4.2.9 on 2024-01-17 01:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("burnplanning", "0013_alter_burnplanelement_status_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="burnplanelement",
            name="justification",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="burnplanning.justification",
            ),
        ),
        migrations.AlterField(
            model_name="burnplanelement",
            name="treatment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="burnplanning.treatment",
            ),
        ),
    ]
