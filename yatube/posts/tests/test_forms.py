import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Comment, Group, Post
from posts.tests import common

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.user_author = mixer.blend(User)

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

    def test_post_create_autorized_client_form(self):
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
        post = Post.objects.get(pk=1)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.text, 'Тестовый пост')
        self.assertTrue(
            post.image.name.endswith('giffy.png'),
        )

    def test_post_create_unautorized_client_form(self):
        """Posts.Forms. Создание нового Post гостем."""
        self.anon.post(
            reverse('posts:post_create'),
            {
                'text': 'Тестовый пост',
            },
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_post_edit_form_author(self):
        """Posts.Forms. редактирование поста автором."""
        self.post = mixer.blend(
            Post,
            author=self.user_author,
            group=self.group,
        )
        context = self.author_client.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            {
                'text': 'Изменение поста',
            },
            follow=True,
        ).context
        self.assertNotEqual(
            context.get('post').text,
            self.post.text,
        )
        self.assertNotEqual(
            context.get('group'),
            self.post.group,
        )

    def test_post_edit_form_auth(self):
        """Posts.Forms. редактирование поста автором."""
        self.post = mixer.blend(
            Post,
            author=self.user_author,
        )
        context = self.auth.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            {
                'text': 'Изменение поста',
            },
            follow=True,
        ).context
        self.assertEqual(
            context.get('post'),
            self.post,
        )
        self.assertEqual(
            context.get('group'),
            self.post.group,
        )

    def test_comments_only_anon_users(self):
        """Созданный коммент отображается на странице post_detail/."""
        post = mixer.blend(Post)
        comment = mixer.blend(Comment, post=post)
        context = self.anon.post(
            reverse('posts:add_comment', args=(comment.post.pk,)),
            {
                'text': 'Комментарий',
            },
            follow=True,
        ).context
        self.assertIsNone(context.get('comment'))

    def test_comments_only_autorized_users(self):
        """Созданный коммент отображается на странице post_detail/."""
        post = mixer.blend(Post)
        comment = mixer.blend(Comment, post=post)
        context = self.auth.post(
            reverse('posts:add_comment', args=(comment.post.pk,)),
            {
                'text': 'Комментарий',
            },
            follow=True,
        ).context
        self.assertEqual(
            context.get('post').comments,
            post.comments,
        )
