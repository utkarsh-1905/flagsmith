# Generated by Django 3.2.20 on 2023-10-18 16:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0046_allow_allowed_projects_to_be_null'),
        ('api_keys', '0003_masterapikey_is_admin'),
        ('users', '0034_add_user_permission_group_membership_through_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalFFAdminUser',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(db_index=True, max_length=254)),
                ('username', models.CharField(blank=True, db_index=True, max_length=150, null=True)),
                ('first_name', models.CharField(max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(max_length=150, verbose_name='last name')),
                ('google_user_id', models.CharField(blank=True, max_length=50, null=True)),
                ('github_user_id', models.CharField(blank=True, max_length=50, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('master_api_key', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='api_keys.masterapikey')),
            ],
            options={
                'verbose_name': 'historical Feature flag admin user',
                'verbose_name_plural': 'historical Feature flag admin users',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalUserPermissionGroup',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('is_default', models.BooleanField(default=False, help_text='If set to true, all new users will be added to this group')),
                ('external_id', models.CharField(blank=True, help_text='Unique ID of the group in an external system', max_length=255, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('master_api_key', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='api_keys.masterapikey')),
                ('organisation', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='organisations.organisation')),
            ],
            options={
                'verbose_name': 'historical user permission group',
                'verbose_name_plural': 'historical user permission groups',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalUserPermissionGroupMembership',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('group_admin', models.BooleanField(default=False)),
                ('m2m_history_id', models.AutoField(primary_key=True, serialize=False)),
                ('ffadminuser', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to='users.historicaluserpermissiongroup')),
                ('userpermissiongroup', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='users.userpermissiongroup')),
            ],
            options={
                'verbose_name': 'HistoricalUserPermissionGroupMembership',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalUserOrganisation',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('date_joined', models.DateTimeField(blank=True, editable=False)),
                ('role', models.CharField(choices=[('ADMIN', 'Admin'), ('USER', 'User')], max_length=50)),
                ('m2m_history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to='users.historicalffadminuser')),
                ('organisation', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='organisations.organisation')),
                ('user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'HistoricalUserOrganisation',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]