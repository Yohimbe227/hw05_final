import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Follow, Group, Post

User = get_user_model()

NUMBER_OF_POSTS = 3
NUMBER_OF_GROUP = 2
NUMBER_OF_USERS = 2
NUMBER_OF_OBJECT_PAGINATOR = 13
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.users = mixer.cycle(NUMBER_OF_USERS).blend(User)
        cls.groups = mixer.cycle(NUMBER_OF_GROUP).blend(Group)
        cls.posts1 = mixer.cycle(NUMBER_OF_POSTS).blend(
            Post,
            author=cls.users[0],
            group=cls.groups[0],
            image=None,
        )
        cls.posts2 = mixer.cycle(NUMBER_OF_POSTS).blend(
            Post,
            author=cls.users[1],
            group=cls.groups[1],
            image=None,
        )
        cls.anon = Client()
        cls.auth = Client()
        cls.auth.force_login(cls.users[0])
        cls.pages_templates_names = (
            (cls.anon, 'posts:index', 'posts/index.html', None),
            (
                cls.anon,
                'posts:group_list',
                'posts/group_list.html',
                (cls.posts1[0].group.slug,),
            ),
            (
                cls.anon,
                'posts:profile',
                'posts/profile.html',
                (cls.posts1[0].author.username,),
            ),
            (
                cls.anon,
                'posts:post_detail',
                'posts/post_detail.html',
                (cls.posts1[0].pk,),
            ),
            (cls.auth, 'posts:post_create', 'posts/create_post.html', None),
            (
                cls.auth,
                'posts:post_edit',
                'posts/create_post.html',
                (cls.posts1[0].pk,),
            ),
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for client, reverse_name, template, args in self.pages_templates_names:
            with self.subTest(reverse_name=reverse_name):
                response = client.get(reverse(reverse_name, args=args))
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.anon.get(reverse('posts:index'))
        cache.clear()
        for i, _ in enumerate(self.posts1 + self.posts2):
            self.assertIsInstance(response.context.get('page_obj')[i], Post)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.anon.get(
            reverse('posts:group_list', args=(self.posts1[0].group.slug,)),
        )
        self.assertEqual(
            set(response.context.get('page_obj').object_list),
            set(self.posts1),
        )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.anon.get(
            reverse('posts:post_detail', args=(self.posts1[0].pk,)),
        )
        self.assertEqual(response.context.get('post'), self.posts1[0])

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.anon.get(
            reverse('posts:profile', args=(self.posts1[0].author.username,)),
        )
        self.assertEqual(
            set(response.context.get('page_obj').object_list),
            set(self.posts1),
        )

    def test_post_create_page_show_correct_context(self):
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

    def test_post_edit_page_show_correct_context(self):
        """Форма в шаблоне post_edit сформирована верно."""
        response = self.auth.get(
            reverse('posts:post_edit', args=(self.posts1[0].pk,)),
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_actions_by_create_post(self):
        """Созданный пост отображается на необходимых страницах."""
        post = mixer.blend(
            Post,
            author=self.users[0],
            group=self.groups[0],
        )
        cache.clear()
        response_profile = self.anon.get(
            reverse('posts:profile', args=(post.author.username,)),
        )
        response_group_list = self.anon.get(
            reverse('posts:group_list', args=(post.group.slug,)),
        )
        response_index = self.anon.get(reverse('posts:index'))
        response_detail = self.anon.get(
            reverse('posts:post_detail', args=(post.pk,))
        )
        posts_on_pages = (
            response_profile.context.get('page_obj'),
            response_group_list.context.get('page_obj'),
            response_index.context.get('page_obj'),
            (response_detail.context.get('post'),),
        )
        for obj in posts_on_pages:
            with self.subTest(obj=obj):
                self.assertEqual(obj[0], post)
                self.assertEqual(obj[0].image, post.image)

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        response = self.anon.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='test_new_post',
            author=self.users[0],
        )
        response_old = self.anon.get(reverse('posts:index'))
        posts_old = response_old.content
        self.assertEqual(posts_old, posts)
        cache.clear()
        response_new = self.anon.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(posts_old, new_posts)

    def test_follows(self):
        Post.objects.all().delete()
        Follow.objects.all().delete()
        user = mixer.blend(User)
        self.anon.post(
            reverse('posts:profile_follow', args=(user.username,)),
        )
        self.assertFalse(Follow.objects.exists())
        self.auth.post(
            reverse('posts:profile_follow', args=(user.username,)),
        )
        self.assertTrue(Follow.objects.exists())
        post_test = mixer.blend(Post, author=user)
        response = self.auth.get(
            reverse('posts:follow_index'),
        )
        post_follow = response.context.get('page_obj')[0]
        self.assertEqual(post_test, post_follow)
        self.auth.post(
            reverse('posts:profile_unfollow', args=(user.username,)),
        )
        self.assertFalse(Follow.objects.exists())


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.posts_per_page = settings.OBJECTS_PER_PAGE
        cls.posts_on_second_page = NUMBER_OF_OBJECT_PAGINATOR - settings.OBJECTS_PER_PAGE
        cls.user = mixer.blend(User)
        cls.anon = Client()
        cls.group = mixer.blend(Group)
        cls.posts = mixer.cycle(NUMBER_OF_OBJECT_PAGINATOR).blend(
            Post,
            author=cls.user,
            group=cls.group,
        )
        cls.page_reverse = (
            ('posts:index', None, ),
            ('posts:group_list', (cls.posts[0].group.slug, )),
            ('posts:profile', (cls.posts[0].author.username,)),
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_paginator(self):
        for page, args in self.page_reverse:
            with self.subTest(page=page):
                response_first = self.anon.get(reverse(page, args=args))
                response_second = self.anon.get(reverse(page, args=args) + '?page=2')
                self.assertEqual(
                    len(response_first.context['page_obj']),
                    self.posts_per_page,
                )
                self.assertEqual(
                    len(response_second.context['page_obj']),
                    self.posts_on_second_page,
                )
