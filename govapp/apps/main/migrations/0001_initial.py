# Generated by Django 4.2.6 on 2023-10-13 06:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import govapp.apps.main.models
import protected_media.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="ModelFile",
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
                ("object_id", models.PositiveIntegerField()),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
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
            options={
                "indexes": [
                    models.Index(
                        fields=["content_type", "object_id"],
                        name="main_modelf_content_194f00_idx",
                    )
                ],
            },
        ),
    ]
