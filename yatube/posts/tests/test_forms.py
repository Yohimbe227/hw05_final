import os
import shutil

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Comment, Group, Post
from posts.tests import common

User = get_user_model()

TEMP_MEDIA_ROOT = os.path.join(settings.MEDIA_ROOT, 'temp')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user, cls.user_author = mixer.cycle(2).blend(User)

        cls.anon = Client()
        cls.auth = Client()
        cls.author_client = Client()

        cls.auth.force_login(cls.user)
        cls.author_client.force_login(cls.user_author)

        cls.group = mixer.blend(Group)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_create_authorized_ok(self) -> None:
        """Posts.Forms. Создание нового Post."""
        self.auth.post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый пост',
                'group': self.group.pk,
                'image': common.image(),
            },
            follow=True,
        )
        self.auth.post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый пост',
                'group': self.group.pk,
                'image': common.image(),
            },
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.get()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.text, 'Тестовый пост')
        self.assertTrue(
            post.image.name.endswith('giffy.png'),
        )

    def test_post_create_ok(self) -> None:
        """Posts.Forms. Создание нового Post гостем."""
        self.anon.post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый пост',
            },
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_post_edit_form_author(self) -> None:
        """Posts.Forms. редактирование поста автором."""
        self.post = mixer.blend(
            Post,
            author=self.user_author,
            group=self.group,
        )
        self.author_client.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            {
                'group': mixer.blend(Group).pk,
                'text': 'Изменение поста',
                'image': common.image(),
            },
            follow=True,
        )
        self.assertNotEqual(
            Post.objects.get(pk=1).group,
            self.post.group,
        )
        self.assertNotEqual(
            Post.objects.get(pk=1).text,
            self.post.text,
        )
        self.assertNotEqual(
            Post.objects.get(pk=1).image.name,
            self.post.image.name,
        )

    def test_post_edit_form_auth(self) -> None:
        """Posts.Forms. редактирование чужого поста."""
        self.post = mixer.blend(
            Post,
            author=self.user_author,
        )
        self.auth.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            {'text': 'Изменение поста', 'group': mixer.blend(Group).pk},
            follow=True,
        )
        self.assertEqual(
            Post.objects.get(pk=1).text,
            self.post.text,
        )
        self.assertEqual(
            Post.objects.get(pk=1).group,
            self.post.group,
        )

    def test_comments_only_anon_users(self) -> None:
        """Созданного коммента нет в базе."""
        post = mixer.blend(Post)
        self.anon.post(
            reverse('posts:add_comment', args=(post.pk,)),
            {
                'text': 'Комментарий',
            },
            follow=True,
        )
        self.assertFalse(Comment.objects.exists())

    def test_comments_only_autorized_users(self) -> None:
        """Созданный коммент отображается на странице post_detail/."""
        post = mixer.blend(Post)
        comment = mixer.blend(Comment, post=post)
        self.auth.post(
            reverse('posts:add_comment', args=(comment.post.pk,)),
            {
                'text': 'Комментарий',
            },
            follow=True,
        )
        self.assertEqual(
            Post.objects.get(pk=1).comments,
            post.comments,
        )

    def test_post_create_page_show_correct_context(self) -> None:
        """Форма в шаблоне post_create сформирована верно."""
        response = self.auth.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
