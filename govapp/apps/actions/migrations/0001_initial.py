# Generated by Django 4.2.8 on 2023-12-14 05:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Action",
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
                    "status",
                    model_utils.fields.StatusField(
                        choices=[("open", "Open"), ("closed", "Closed")],
                        default="open",
                        max_length=100,
                        no_check_for_status=True,
                        verbose_name="status",
                    ),
                ),
                (
                    "status_changed",
                    model_utils.fields.MonitorField(
                        default=django.utils.timezone.now,
                        monitor="status",
                        verbose_name="status changed",
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("pre-treatment", "Pre-treatment"),
                            ("day-of-treatment", "Day of treatment"),
                            ("post-treatment", "Post-treatment"),
                        ],
                        max_length=255,
                    ),
                ),
                ("action", models.CharField(max_length=255, unique=True)),
                ("date_created", models.DateField(auto_now_add=True)),
                ("date_closed", models.DateField(blank=True, null=True)),
                ("closed_details", models.TextField(blank=True, null=True)),
                ("due_date_time", models.DateTimeField(blank=True, null=True)),
                (
                    "closed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="closed_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
