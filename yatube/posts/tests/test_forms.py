import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.forms import PostForm
from posts.models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = mixer.blend(Group)
        cls.form_data = {
            'text': 'Тестовый пост',
            'group': cls.group.pk,
        }
        cls.user = mixer.blend(User)
        cls.anon = Client()
        cls.auth = Client()
        cls.auth.force_login(cls.user)
        cls.user_author = mixer.blend(User)
        cls.author_client = Client()
        cls.author_client.force_login(cls.user_author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_create_autorized_client_form(self):
        """Posts.Forms. Создание нового Post."""
        Post.objects.all().delete()
        self.auth.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.all()[0].author, self.user)
        self.assertEqual(Post.objects.all()[0].group, self.group)
        self.assertEqual(Post.objects.all()[0].text, self.form_data['text'])

    def test_post_create_unautorized_client_form(self):
        """Posts.Forms. Создание нового Post гостем."""
        Post.objects.all().delete()
        self.anon.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), 0)

    def test_post_edit_form(self):
        """Posts.Forms. редактирование поста автором."""
        self.post = mixer.blend(
            Post,
            author=self.user_author,
            group=self.group,
        )
        user_author2 = mixer.blend(User)
        author_client2 = Client()
        author_client2.force_login(user_author2)
        self.form_data['text'] = 'Изменение поста'
        response_author1 = self.author_client.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            data=self.form_data,
            follow=True,
        )
        response_author2 = author_client2.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            data=self.form_data,
            follow=True,
        )
        self.assertNotEqual(
            response_author1.context.get('post').text,
            self.post.text,
        )
        self.assertNotEqual(
            response_author1.context.get('group'),
            self.post.group,
        )
        self.assertEqual(
            response_author2.context.get('post'),
            self.post,
        )

    def test_comments_only_autorized_users(self):
        """Созданный коммент отображается на странице post_detail/."""
        comment = mixer.blend(Comment, post__text='test_text')
        self.form_data['text'] = 'Комментарий'
        response_anon = self.anon.post(
            reverse('posts:add_comment', args=(comment.post.pk,)),
            data=self.form_data,
            follow=True,
        )
        response_auth = self.auth.post(
            reverse('posts:add_comment', args=(comment.post.pk,)),
            data=self.form_data,
            follow=True,
        )
        self.assertIsNone(response_anon.context.get('comments'))
        self.assertTrue(response_auth.context.get('comments').exists())


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.group = mixer.blend(Group)
        cls.post = mixer.blend(Post, group=cls.group)
        cls.form = PostForm()
        cls.auth = Client()
        cls.auth.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_image_add(self):
        """Проверка добавления картинок"""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif', content=small_gif, content_type='image/gif'
        )
        form_data = {
            'group': self.post.group.pk,
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        self.auth.post(reverse('posts:index'), data=form_data, follow=True)
        self.assertTrue(Post.objects.filter(pk=self.post.group.pk).exists())
