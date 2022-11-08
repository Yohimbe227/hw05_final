from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from mixer.backend.django import mixer

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.group = mixer.blend(Group, slug='test_slug')
        cls.anon = Client()
        cls.auth = Client()
        cls.auth.force_login(cls.user)
        cls.user_author = mixer.blend(User)
        cls.author_client = Client()
        cls.author_client.force_login(cls.user_author)
        cls.post = mixer.blend(Post, author=cls.user_author)
        cls.public_url = (
            ('/', 'posts/index.html'),
            (f'/group/{cls.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{cls.user.username}/', 'posts/profile.html'),
            (f'/posts/{cls.post.pk}/', 'posts/post_detail.html'),
        )
        cls.private_url = (
            ('/create/', 'posts/create_post.html'),
            (f'/posts/{cls.post.pk}/edit/', 'posts/create_post.html'),
        )

    def test_public_urls_uses_correct_template_OK(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in self.public_url:
            with self.subTest(address=address):
                response = self.anon.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_urls_uses_correct_template_OK(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in self.private_url:
            with self.subTest(address=address):
                response_author = self.author_client.get(address)
                response_guest = self.anon.get(address)
                self.assertTemplateUsed(response_author, template)
                self.assertEqual(response_author.status_code, HTTPStatus.OK)
                self.assertEqual(response_guest.status_code, HTTPStatus.FOUND)

    def test_post_edit_url(self):
        """Не автор не может редактировать пост"""
        response_auth = self.auth.get(self.private_url[1][0])
        self.assertEqual(response_auth.status_code, HTTPStatus.FOUND)

    def test_post_not_exists_url(self):
        """Страница /unexisting_page/ доступна любому пользователю."""
        response = self.anon.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
