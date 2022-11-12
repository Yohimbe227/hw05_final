from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer

from posts.models import Follow, Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = mixer.blend(Group, slug='test_slug')
        cls.post = mixer.blend(Post)
        cls.follow = mixer.blend(Follow)

        cls.user = mixer.blend(User)
        cls.user_author = mixer.blend(User)

        cls.anon = Client()
        cls.auth = Client()
        cls.author_client = Client()

        cls.auth.force_login(cls.user)
        cls.author_client.force_login(cls.user_author)
        cls.post = mixer.blend(Post, author=cls.user_author)

        cls.public_url = (
            ('posts:index', 'posts/index.html', None),
            (
                'posts:group_list',
                'posts/group_list.html',
                (cls.group.slug,),
            ),
            (
                'posts:profile',
                'posts/profile.html',
                (cls.user.username,),
            ),
            (
                'posts:post_detail',
                'posts/post_detail.html',
                (cls.post.pk,),
            ),
        )
        cls.private_url = (
            ('posts:post_create', 'posts/create_post.html', None),
            (
                'posts:post_edit',
                'posts/create_post.html',
                (cls.post.pk,),
            ),
            ('posts:follow_index', 'posts/follow.html', None),
        )
        cls.redirect_url = (
            (
                reverse('posts:add_comment', args=(cls.post.pk,)),
                reverse('posts:post_detail', args=(cls.post.pk,)),
            ),
            (
                reverse('posts:profile_follow', args=(cls.user.username,)),
                reverse('posts:profile', args=(cls.user.username,)),
            ),
            (
                reverse('posts:profile_unfollow', args=(cls.user.username,)),
                reverse('posts:profile', args=(cls.user_author.username,)),
            ),
        )

    def test_public_urls_uses_correct_template_OK(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template, args in self.public_url:
            with self.subTest(address=address):
                response = self.anon.get(reverse(address, args=args))
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_urls_uses_correct_template_OK(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template, args in self.private_url:
            with self.subTest(address=address):
                response_author = self.author_client.get(
                    reverse(address, args=args,)
                )
                response_guest = self.anon.get(reverse(address, args=args))
                self.assertTemplateUsed(response_author, template)
                self.assertEqual(response_author.status_code, HTTPStatus.OK)
                self.assertEqual(response_guest.status_code, HTTPStatus.FOUND)

    def test_post_edit_url(self):
        """Не автор не может редактировать пост"""
        self.assertEqual(
            self.auth.get(
                reverse('posts:post_edit', args=(self.post.pk,),)
            ).status_code,
            HTTPStatus.FOUND,
        )

    def test_post_not_exists_url(self):
        """Страница /unexisting_page/ доступна любому пользователю."""
        self.assertEqual(
            self.anon.get('/unexisting_page/').status_code,
            HTTPStatus.NOT_FOUND,
        )

    def test_redirect(self):
        """Тестирование редиректов"""
        for adress, expected in self.redirect_url:
            with self.subTest(address=adress):
                self.assertRedirects(self.author_client.get(adress), expected)
