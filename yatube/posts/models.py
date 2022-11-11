from django.contrib.auth import get_user_model
from django.db import models

from core.models import DefaultModel, TimestampedModel
from core.utils import cut_text

User = get_user_model()


class Group(DefaultModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='группа')

    def __str__(self) -> str:
        return cut_text(self.title)


class Post(DefaultModel):
    text = models.TextField(
        verbose_name='текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='группа',
        help_text='Группа, к которой будет относиться пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        null=True,
    )
    image = models.ImageField('картинка', upload_to='posts/', blank=True)

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'posts'
        verbose_name = 'пост'

    def __str__(self) -> str:
        return cut_text(self.text)


class Comment(TimestampedModel):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='пост',
        help_text='Ваш комментарий',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        null=True,
    )
    text = models.TextField(
        verbose_name='текст комментария',
        help_text='Введите текст комментария',
    )

    class Meta:
        ordering = ('-created',)
        default_related_name = 'comments'
        verbose_name = 'comment'

    def __str__(self) -> str:
        return f'Комментарий {self.author} на {self.post}'


class Follow(DefaultModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
        null=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор',
        null=True,
    )

    def __str__(self) -> str:
        return f'Подписался {self.user} на {self.author}'
