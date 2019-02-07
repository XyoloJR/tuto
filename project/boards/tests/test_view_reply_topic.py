from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from ..models import Board, Topic, Post
from ..views import reply_topic
from ..forms import PostForm


class ReplyTopicTestCase(TestCase):
    '''
    Base test case to be used in all 'reply_topic' view tests
    '''
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board')
        self.username = 'john'
        self.password = '123'
        user = User.objects.create_user(username=self.username, email='john@doe.com', password=self.password)

        self.topic = Topic.objects.create(subject='tuto', board=self.board, starter=user)

        Post.objects.create(
            message='message',
            topic=self.topic,
            created_by=user
        )

        self.url = reverse('reply_topic', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})


class LoginRequiredReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(
            self.response,
            '{login_url}?next={url}'.format(login_url=login_url, url=self.url)
        )


class ReplyTopicViewTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
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

    def test_new_topic_view_contains_link_back_to_topic_posts_view(self):
        topic_posts_url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        self.assertContains(self.response, 'href="{0}"'.format(topic_posts_url))

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PostForm)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')


class SuccessfulReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)

    def test_reply_topic_valid_post_data(self):
        data = {
            'message': '''
            Test message content with a pretty long text. see... i\'m not joking  when I talk about long text. 
            And that is just the beginning of it. The limit is actually of four thousend chars
            '''
        }
        self.client.post(self.url, data)
        self.assertEquals(Post.objects.count(), 2)


class InvalidReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)

    def test_new_topic_invalid_post_data(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation error
        '''
        response = self.client.post(self.url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_new_topic_invalid_post_data_empty_fields(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation error
        '''
        data = {
            'message': '',
        }

        response = self.client.post(self.url, data)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(Post.objects.count(), 1)



