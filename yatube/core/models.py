from django.db import models


class DefaultModel(models.Model):
    text = models.TextField(
        verbose_name='текст комментария',
        help_text='Введите текст комментария',
    )

    class Meta:
        abstract = True
