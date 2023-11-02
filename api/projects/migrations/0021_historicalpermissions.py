# Generated by Django 3.2.20 on 2023-11-02 18:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_historicalmodels'),
        ('api_keys', '0003_masterapikey_is_admin'),
        ('permissions', '0009_move_view_audit_log_permission'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0020_historicalproject'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalUserPermissionGroupProjectPermission',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('admin', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('group', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='users.userpermissiongroup')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('master_api_key', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='api_keys.masterapikey')),
                ('project', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', related_query_name='grouppermission', to='projects.project')),
            ],
            options={
                'verbose_name': 'historical user permission group project permission',
                'verbose_name_plural': 'historical user permission group project permissions',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalUserProjectPermission',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('admin', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('master_api_key', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='api_keys.masterapikey')),
                ('project', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', related_query_name='userpermission', to='projects.project')),
                ('user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical user project permission',
                'verbose_name_plural': 'historical user project permissions',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalUserProjectPermission_permissions',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('m2m_history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to='projects.historicaluserprojectpermission')),
                ('permissionmodel', models.ForeignKey(blank=True, db_constraint=False, db_tablespace='', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='permissions.permissionmodel')),
                ('userprojectpermission', models.ForeignKey(blank=True, db_constraint=False, db_tablespace='', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='projects.userprojectpermission')),
            ],
            options={
                'verbose_name': 'HistoricalUserProjectPermission_permissions',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalUserPermissionGroupProjectPermission_permissions',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('m2m_history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to='projects.historicaluserpermissiongroupprojectpermission')),
                ('permissionmodel', models.ForeignKey(blank=True, db_constraint=False, db_tablespace='', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='permissions.permissionmodel')),
                ('userpermissiongroupprojectpermission', models.ForeignKey(blank=True, db_constraint=False, db_tablespace='', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='projects.userpermissiongroupprojectpermission')),
            ],
            options={
                'verbose_name': 'HistoricalUserPermissionGroupProjectPermission_permissions',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
