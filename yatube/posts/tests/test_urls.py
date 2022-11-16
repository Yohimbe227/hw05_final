from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.user_author = mixer.blend(User)
        cls.group = mixer.blend(Group, slug='test_slug')
        cls.post = mixer.blend(Post, author=cls.user_author)

        # cls.follow = mixer.blend(Follow)

        cls.anon = Client()
        cls.auth = Client()
        cls.author_client = Client()

        cls.auth.force_login(cls.user)
        cls.author_client.force_login(cls.user_author)
        cls.post = mixer.blend(Post, author=cls.user_author, group=cls.group)

        cls.urls = {
            'group': reverse('posts:group_list', args=(cls.group.slug,)),
            'index': reverse('posts:index'),
            'profile': reverse('posts:profile', args=(cls.user.username,)),
            'detail': reverse('posts:post_detail', args=(cls.post.pk,)),
            'post-create': reverse('posts:post_create'),
            'post-edit': reverse('posts:post_edit', args=(cls.post.pk,)),
            'follow-index': reverse('posts:follow_index'),
            'comment': reverse('posts:add_comment', args=(cls.post.pk,)),
            'follow': reverse(
                'posts:profile_follow', args=(cls.user.username,)
            ),
            'unfollow': reverse(
                'posts:profile_unfollow', args=(cls.user.username,)
            ),
            'missing': 'core.views.page_not_found',
        }

    def test_http_statuses(self) -> None:
        httpstatuses = (
            (self.urls.get('detail'), HTTPStatus.OK, self.anon),
            (self.urls.get('group'), HTTPStatus.OK, self.anon),
            (self.urls.get('follow-index'), HTTPStatus.OK, self.auth),
            (self.urls.get('follow-index'), HTTPStatus.FOUND, self.anon),
            (self.urls.get('follow'), HTTPStatus.FOUND, self.auth),
            (self.urls.get('index'), HTTPStatus.OK, self.anon),
            (self.urls.get('missing'), HTTPStatus.NOT_FOUND, self.anon),
            (self.urls.get('post-create'), HTTPStatus.OK, self.auth),
            (self.urls.get('post-create'), HTTPStatus.FOUND, self.anon),
            (self.urls.get('post-edit'), HTTPStatus.OK, self.author_client),
            (self.urls.get('post-edit'), HTTPStatus.FOUND, self.auth),
            (self.urls.get('post-edit'), HTTPStatus.FOUND, self.anon),
            (self.urls.get('profile'), HTTPStatus.OK, self.anon),
            (self.urls.get('unfollow'), HTTPStatus.FOUND, self.anon),
        )

        for url, status, client in httpstatuses:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, status)

    def test_templates(self) -> None:
        templates = (
            (self.urls.get('detail'), 'posts/post_detail.html', self.anon),
            (self.urls.get('group'), 'posts/group_list.html', self.anon),
            (self.urls.get('follow-index'), 'posts/follow.html', self.auth),
            (self.urls.get('index'), 'posts/index.html', self.anon),
            (self.urls.get('missing'), 'core/404.html', self.anon),
            (self.urls.get('post-edit'), 'posts/create_post.html', self.author_client),
            (self.urls.get('profile'), 'posts/profile.html', self.anon),
        )
        for url, template, client in templates:
            with self.subTest(url=url):
                self.assertTemplateUsed(client.get(url), template)

    def test_redirects(self) -> None:
        redirects = (
                (self.urls.get('follow-index'), f'/auth/login/?next={self.urls.get("follow-index")}', self.anon,),
                (self.urls.get('post-create'), f'/auth/login/?next={self.urls.get("post-create")}', self.anon,),
                (self.urls.get('post-edit'), f'/posts/{self.post.pk}/', self.auth,),
                (self.urls.get('post-edit'), f'/auth/login/?next={self.urls.get("post-edit")}', self.anon,),
        )
        for url, redirect, client in redirects:
            with self.subTest(url=url):
                self.assertRedirects(client.get(url), redirect)
