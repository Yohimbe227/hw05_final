# Generated by Django 2.2.19 on 2022-11-09 09:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0017_auto_20221109_1229"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="post",
            options={
                "default_related_name": "posts",
                "ordering": ("-pub_date",),
                "verbose_name": "пост",
            },
        ),
    ]
