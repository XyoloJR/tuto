from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve

from ..forms import forms
from ..models import Board, Post, Topic
from ..views import PostUpdateView


class PostUpdateViewTestCase(TestCase):
    '''
    Base test case to be used in all 'update_post' view tests
    '''

    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board')
        self.username = 'john'
        self.password = '123'
        user = User.objects.create_user(username=self.username, email='john@doe.com', password=self.password)

        self.topic = Topic.objects.create(subject='tuto', board=self.board, starter=user)

        self.post = Post.objects.create(
            message='''
                    Test message content with a pretty long text. see... i\'m not joking  when I talk about long text. 
                    And that is just the beginning of it. The limit is actually of four thousend chars
                    ''',
            topic=self.topic,
            created_by=user
        )

        self.url = reverse(
            'update_post',
            kwargs={'pk': self.board.pk,
                    'topic_pk': self.topic.pk,
                    'post_pk': self.post.pk})


class LoginRequiredPostUpdateViewTests(PostUpdateViewTestCase):
    def test_redirection(self):
        '''
        Test if only logged in users can edit the posts
        '''
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{0}?next={1}'.format(login_url, self.url))


class UnauthorizedPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        '''
        Create a new user different from the one who posted
        '''
        super().setUp()
        username = 'jane'
        password = '321'
        user = User.objects.create_user(username=username, email='jane@doe.com', password=password)
        self.client.login(username=username, password=password)
        self.response = self.client.get(self.url)

    def test_status_code(self):
        '''
        A Post should be edited only by the owner.
        Unauthorized users should get a 404 response (Page Not Found)
        '''
        self.assertEquals(self.response.status_code, 404)


class PostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_not_found_status_code(self):
        url = reverse(
            'update_post',
            kwargs={'pk': self.board.pk,
                    'topic_pk': self.topic.pk,
                    'post_pk': 10})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_view_class(self):
        view = resolve('/boards/1/topics/1/posts/1/')
        self.assertEquals(view.func.view_class, PostUpdateView)

    def test_contains_link_back_to_topic_posts_view(self):
        topic_posts_url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        self.assertContains(self.response, 'href="{0}"'.format(topic_posts_url))

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, forms.ModelForm)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_form_inputs(self):
        '''
        The view must contain two inputs: csrf, message textarea
        '''
        self.assertContains(self.response, '<input', 1)
        self.assertContains(self.response, '<textarea', 1)


class SuccessfulPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        data = {'message': self.post.message + 'edition tag'}
        self.response = self.client.post(self.url, data)

    def test_redirection(self):
        expected_url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        self.assertRedirects(self.response, expected_url)

    def test_no_additional_post_created(self):
        self.assertEquals(Post.objects.count(), 1)

    def test_edition_text_added(self):
        self.post.refresh_from_db()
        self.assertIn('edition tag', self.post.message)


class InvalidPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        '''
        Submit an empty dictionary to the 'reply'_topic view
        '''
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})

    def test_status_code(self):
        '''
        An invalid form submission should return to the same page
        '''
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        '''
        Should return error message
        '''
        form = self.response.context.get('form')
        self.assertTrue(form.errors)
