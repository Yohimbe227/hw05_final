import os
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Follow, Group, Post

User = get_user_model()

NUMBER_OF_POSTS = 3
NUMBER_OF_OBJECT_PAGINATOR = 13
TEMP_MEDIA_ROOT = os.path.join(settings.MEDIA_ROOT, "temp")


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user, cls.user_author = mixer.cycle(2).blend(User)
        cls.group, cls.group2 = mixer.cycle(2).blend(Group)

        cls.anon = Client()
        cls.auth = Client()

        cls.auth.force_login(cls.user_author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        cache.clear()

    def test_home_page_show_correct_context(self) -> None:
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        mixer.blend(Post)
        response = self.anon.get(reverse("posts:index"))
        cache.clear()
        self.assertIsInstance(response.context.get("page_obj")[0], Post)

    def test_group_list_page_show_correct_context(self) -> None:
        """Шаблон group_list сформирован с правильным контекстом."""
        post = mixer.blend(Post, group=self.group)
        response = self.anon.get(
            reverse("posts:group_list", args=(self.group.slug,)),
        )
        self.assertEqual(
            response.context.get("page_obj")[0],
            post,
        )

    def test_post_detail_page_show_correct_context(self) -> None:
        """Шаблон post_detail сформирован с правильным контекстом."""
        post = mixer.blend(Post, group=self.group)
        response = self.anon.get(
            reverse("posts:post_detail", args=(post.pk,)),
        )
        self.assertEqual(response.context.get("post"), post)

    def test_profile_page_show_correct_context(self) -> None:
        """Шаблон profile сформирован с правильным контекстом."""
        post = mixer.blend(Post, group=self.group)
        response = self.anon.get(
            reverse("posts:profile", args=(post.author.username,)),
        )
        self.assertEqual(
            response.context.get("page_obj")[0],
            post,
        )

    def test_actions_by_create_post(self) -> None:
        """Созданный пост отображается на необходимых страницах."""
        post = mixer.blend(
            Post,
            author=self.user,
            group=self.group,
        )
        response_profile = self.anon.get(
            reverse("posts:profile", args=(post.author.username,)),
        )
        response_group_list = self.anon.get(
            reverse("posts:group_list", args=(post.group.slug,)),
        )
        cache.clear()
        response_index = self.anon.get(reverse("posts:index"))
        response_detail = self.anon.get(
            reverse(
                "posts:post_detail",
                args=(post.pk,),
            ),
        )
        posts_on_pages = (
            response_profile.context.get("page_obj"),
            response_group_list.context.get("page_obj"),
            response_index.context.get("page_obj"),
            (response_detail.context.get("post"),),
        )
        for obj in posts_on_pages:
            with self.subTest(obj=obj):
                self.assertEqual(obj[0], post)
                self.assertEqual(obj[0].image, post.image)

    def test_cache_index(self) -> None:
        """Проверка хранения и очищения кэша для index."""
        posts = self.anon.get(reverse("posts:index")).content
        mixer.blend(
            Post,
            text="test_new_post",
            author=self.user,
        )
        posts_old = self.anon.get(reverse("posts:index")).content
        self.assertEqual(posts_old, posts)
        cache.clear()
        posts_new = self.anon.get(reverse("posts:index")).content
        self.assertNotEqual(posts_old, posts_new)

    def test_follows(self) -> None:
        self.anon.post(
            reverse("posts:profile_follow", args=(self.user.username,)),
        )
        self.assertFalse(Follow.objects.exists())
        self.auth.post(
            reverse("posts:profile_follow", args=(self.user.username,)),
        )
        self.assertTrue(Follow.objects.exists())
        post_test = mixer.blend(Post, author=self.user)
        response = self.auth.get(
            reverse("posts:follow_index"),
        )
        post_follow = response.context.get("page_obj")[0]
        self.assertEqual(post_test, post_follow)
        self.auth.post(
            reverse("posts:profile_unfollow", args=(self.user.username,)),
        )
        self.assertFalse(Follow.objects.exists())

    def test_paginator(self) -> None:
        posts_per_page = settings.OBJECTS_PER_PAGE

        posts_on_second_page = NUMBER_OF_OBJECT_PAGINATOR - settings.OBJECTS_PER_PAGE
        posts = mixer.cycle(NUMBER_OF_OBJECT_PAGINATOR).blend(
            Post,
            author=self.user,
            group=self.group,
        )
        page_reverse = (
            (
                "posts:index",
                None,
            ),
            ("posts:group_list", (posts[0].group.slug,)),
            ("posts:profile", (posts[0].author.username,)),
        )
        for page, args in page_reverse:
            with self.subTest(page=page):
                cache.clear()
                response_first = self.anon.get(reverse(page, args=args))
                response_second = self.anon.get(
                    reverse(page, args=args) + "?page=2",
                )
                cache.clear()
                self.assertEqual(
                    len(response_first.context["page_obj"]),
                    posts_per_page,
                )
                self.assertEqual(
                    len(response_second.context["page_obj"]),
                    posts_on_second_page,
                )
