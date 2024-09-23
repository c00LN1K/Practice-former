# Generated by Django 5.1.1 on 2024-09-22 14:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_second_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studygroup',
            name='leader',
            field=models.OneToOneField(blank=True, max_length=50, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='group_leader', to=settings.AUTH_USER_MODEL, verbose_name='Староста'),
        ),
    ]
