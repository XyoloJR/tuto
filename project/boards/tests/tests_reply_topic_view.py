from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.urls import resolve

from ..models import Board, Topic, Post
from ..views import reply_topic


class ReplyTopicViewTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board')
        user = User.objects.create_user(username='john', email='john@doe.com', password='123')
        self.topic = Topic.objects.create(subject='tuto', board=self.board, starter=user)

        self.url = reverse('reply_topic', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        self.response = self.client.get(self.url)

    def test_reply_topic_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_reply_topic_view_not_found_status_code(self):
        url = reverse('reply_topic', kwargs={'pk': self.board.pk, 'topic_pk': 10})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_reply_topic_url_resolves_new_topic_view(self):
        view = resolve('/boards/1/topics/1/reply/')
        self.assertEquals(view.func, reply_topic)

    # def test_new_topic_view_contains_link_back_to_board_topics_view(self):
    #     board_topics_url = reverse('board_topics', kwargs={'pk': self.board.pk})
    #     self.assertContains(self.response, 'href="{0}"'.format(board_topics_url))
