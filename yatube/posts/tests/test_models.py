from unittest import TestCase

from django.test import TestCase
from mixer.backend.django import mixer

from core import utils
from posts.models import Group, Post, Comment, Follow


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
        cls.post = mixer.blend(Post)

    def test_model_post_have_correct_object_names(self):
        """У Post корректно работает __str__."""
        self.assertEqual(
            utils.cut_text(self.post.text), utils.cut_text(str(self.post))
        )


class CommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.comment = mixer.blend(Comment)

    def test_model_post_have_correct_object_names(self):
        """У Comment корректно работает __str__."""
        self.assertEqual(
            f'Комментарий {self.comment.author} к {self.comment.post}',
            str(self.comment),
        )


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follow = mixer.blend(Follow)

    def test_model_post_have_correct_object_names(self):
        """У Follow корректно работает __str__."""
        self.assertEqual(
            f'Подписался {self.follow.user} на {self.follow.author}',
            str(self.follow),
        )
