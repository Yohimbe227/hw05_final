# Generated by Django 3.2.16 on 2022-10-29 12:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("posts", "0005_alter_group_slug"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="post",
            options={
                "default_related_name": "posts",
                "ordering": ("-pub_date",),
            },
        ),
        migrations.AlterField(
            model_name="group",
            name="description",
            field=models.TextField(verbose_name="Группа"),
        ),
        migrations.AlterField(
            model_name="post",
            name="author",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="posts",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="group",
            field=models.ForeignKey(
                blank=True,
                help_text="Группа, к которой будет относиться пост",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="posts",
                to="posts.group",
                verbose_name="Группа",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="text",
            field=models.TextField(
                help_text="Введите текст поста", verbose_name="Текст поста"
            ),
        ),
    ]
