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

    def setUp(self):
        self.form_data = {
            'text': 'Тестовый пост',
            'group': self.group.pk,
            'image': common.image(),
        }

    def test_post_create_autorized_client_form(self):
        """Posts.Forms. Создание нового Post."""
        self.auth.post(
            reverse('posts:post_create'),
            self.form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get(pk=1).author, self.user)
        self.assertEqual(Post.objects.get(pk=1).group, self.group)
        self.assertEqual(Post.objects.get(pk=1).text, self.form_data['text'])
        self.assertTrue(
            Post.objects.get(pk=1).image.name.endswith('giffy.png'),
        )

    def test_post_create_unautorized_client_form(self):
        """Posts.Forms. Создание нового Post гостем."""
        self.anon.post(
            reverse('posts:post_create'),
            self.form_data,
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
        self.form_data['text'] = 'Изменение поста'
        response = self.author_client.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            self.form_data,
            follow=True,
        )
        self.assertNotEqual(
            response.context.get('post').text,
            self.post.text,
        )
        self.assertNotEqual(
            response.context.get('group'),
            self.post.group,
        )

    def test_post_edit_form_auth(self):
        """Posts.Forms. редактирование поста автором."""
        self.post = mixer.blend(
            Post,
            author=self.user_author,
        )
        self.form_data['text'] = 'Изменение поста'
        response = self.auth.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            self.form_data,
            follow=True,
        )
        self.assertEqual(
            response.context.get('post'),
            self.post,
        )
        self.assertEqual(
            response.context.get('group'),
            self.post.group,
        )

    def test_comments_only_anon_users(self):
        """Созданный коммент отображается на странице post_detail/."""
        comment = mixer.blend(Comment, post__text='test_text')
        self.form_data['text'] = 'Комментарий'
        response_anon = self.anon.post(
            reverse('posts:add_comment', args=(comment.post.pk,)),
            self.form_data,
            follow=True,
        )
        self.assertIsNone(response_anon.context.get('comment'))

    def test_comments_only_autorized_users(self):
        """Созданный коммент отображается на странице post_detail/."""
        post = mixer.blend(Post)
        comment = mixer.blend(Comment, post=post)
        self.form_data['text'] = 'Комментарий'
        response_auth = self.auth.post(
            reverse('posts:add_comment', args=(comment.post.pk,)),
            self.form_data,
            follow=True,
        )
        self.assertEqual(
            response_auth.context.get('post').comments,
            post.comments,
        )

    def test_image_add(self):
        """Проверка добавления картинок"""
        post = mixer.blend(Post, group=self.group)
        self.auth.post(
            reverse('posts:index'),
            data={
                'group': post.pk,
                'text': 'Тестовый текст',
                'image': common.image(),
            },
            follow=True,
        )
        self.assertEqual(Post.objects.get(pk=post.pk).group, post.group)
        self.assertEqual(Post.objects.get(pk=post.pk).text, post.text)
        self.assertEqual(
            Post.objects.get(pk=post.pk).image.name,
            post.image.name,
        )
