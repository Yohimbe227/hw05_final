# Generated by Django 2.2.19 on 2022-11-07 09:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0014_auto_20221105_1741'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follow',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('created', models.DateTimeField(auto_now_add=True)),
                (
                    'author',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='following',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='автор',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='follower',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='подписчик',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
        ),
    ]