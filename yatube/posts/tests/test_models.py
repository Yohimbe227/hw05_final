from django.contrib.auth import get_user_model
from django.test import TestCase
from mixer.backend.django import mixer

from posts.models import Group, Post

User = get_user_model()


class GroupTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = mixer.blend(Group, title='Тестовая группа')

    def test_model_post_have_correct_object_names(self):
        """У Group корректно работает __str__."""
        self.assertEqual(self.group.title, str(self.group))


class PostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = mixer.blend(User)
        cls.post = mixer.blend(Post, author=cls.user, text='Тестовый пост')

    def test_model_post_have_correct_object_names(self):
        """У Post корректно работает __str__."""
        self.assertEqual(self.post.text, str(self.post))
