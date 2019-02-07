from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from ..models import Board, Post, Topic
from ..views import topic_posts


# Create your tests here.
class LoginRequiredTopicPostsTests(TestCase):
    def setUp(self):
        board = Board.objects.create(name='Django', description='Django board')
        user = User.objects.create_user(username='john', email='john@doe.com', password='1234pass')
        topic = Topic.objects.create(subject='Hello, world', board=board, starter=user)
        self.url = reverse('topic_posts', kwargs={'pk': board.pk, 'topic_pk': topic.pk})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(
            self.response,
            '{login_url}?next={url}'.format(login_url=login_url, url=self.url)
        )


class TopicPostsTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='john', email='john@doe.com', password='1234pass')
        self.client.login(username='john', password='1324pass')
        board = Board.objects.create(name='Django', description='Django board')
        topic = Topic.objects.create(subject='Hello, world', board=board, starter=user)
        Post.objects.create(message='Le premier post de l appli', topic=topic, created_by=user)

        url = reverse('topic_posts', kwargs={'pk': board.pk, 'topic_pk': topic.pk})
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/boards/1/topics/1/')
        self.assertEquals(view.func, topic_posts)
