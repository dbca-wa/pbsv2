# Generated by Django 4.2.6 on 2023-10-13 06:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import govapp.apps.main.models
import protected_media.models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="File",
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
                    "file",
                    protected_media.models.ProtectedFileField(
                        storage=protected_media.models.ProtectedFileSystemStorage(),
                        upload_to=govapp.apps.main.models.file_upload_location,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                ("datetime_uploaded", models.DateTimeField(auto_now_add=True)),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="ModelFile",
        ),
    ]
