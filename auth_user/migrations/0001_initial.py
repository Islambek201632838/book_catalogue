# Generated by Django 5.0.7 on 2024-07-25 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True, verbose_name='email address')),
                ('first_name', models.CharField(db_index=True, max_length=30)),
                ('last_name', models.CharField(db_index=True, max_length=30)),
                ('gender', models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female')], db_index=True, max_length=6)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'indexes': [models.Index(fields=['email'], name='auth_user_c_email_cdf273_idx'), models.Index(fields=['first_name'], name='auth_user_c_first_n_3dbcbc_idx'), models.Index(fields=['last_name'], name='auth_user_c_last_na_49f5c2_idx'), models.Index(fields=['is_active'], name='auth_user_c_is_acti_a34aac_idx')],
            },
        ),
    ]