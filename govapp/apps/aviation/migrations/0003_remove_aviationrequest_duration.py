# Generated by Django 4.2.6 on 2023-10-13 04:29

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("aviation", "0002_aviationrequest_status_changed_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="aviationrequest",
            name="duration",
        ),
    ]
