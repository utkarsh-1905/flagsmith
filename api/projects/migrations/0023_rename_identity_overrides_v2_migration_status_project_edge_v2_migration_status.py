# Generated by Django 3.2.25 on 2024-05-02 12:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0022_add_stale_flags_threshold_to_project"),
    ]

    operations = [
        migrations.RenameField(
            model_name="project",
            old_name="identity_overrides_v2_migration_status",
            new_name="edge_v2_migration_status",
        ),
    ]
