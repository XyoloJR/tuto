from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from ..models import Board, Post, Topic
from ..views import PostListView


class TopicPostsTestCase(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board')
        self.user = User.objects.create_user(username='john', email='john@doe.com', password='1234pass')
        self.topic = Topic.objects.create(subject='Hello, world', board=self.board, starter=self.user)

        Post.objects.create(message='Le premier post de l appli', topic=self.topic, created_by=self.user)
        self.url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})


# Create your tests here.
class LoginRequiredTopicPostsTests(TopicPostsTestCase):
    def setUp(self):
        super().setUp()
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(
            self.response,
            '{login_url}?next={url}'.format(login_url=login_url, url=self.url)
        )


class TopicPostsTests(TopicPostsTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='john', password='1234pass')
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/boards/1/topics/1/')
        self.assertEquals(view.func.view_class, PostListView)
