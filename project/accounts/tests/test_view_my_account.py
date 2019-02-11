from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve

from ..views import UserUpdateView


class MyAccountTestCase(TestCase):
    '''
    Base test case to be used in all 'reply_topic' view tests
    '''

    def setUp(self):
        self.username = 'john'
        self.password = '123'
        self.user = User.objects.create_user(username=self.username, email='john@doe.com', password=self.password)

        self.url = reverse('my_account')


class LoginRequiredReplyTopicTests(MyAccountTestCase):
    def test_redirection(self):
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            '{login_url}?next={url}'.format(login_url=login_url, url=self.url)
        )


class MyAccountViewTests(MyAccountTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_class_view(self):
        view = resolve('/settings/account/')
        self.assertEquals(view.func.view_class, UserUpdateView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_form_inputs(self):
        '''
        The view must contain two inputs: csrf, message textarea
        '''
        self.assertContains(self.response, '<input', 4)
        self.assertContains(self.response, 'type="text"', 2)
        self.assertContains(self.response, 'type="email"', 1)


class SuccessfulChangesTests(MyAccountTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.first_name = 'john'
        self.last_name = 'doe'
        self.new_email = 'jdoe@doe.com'
        data = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.new_email
        }
        self.response = self.client.post(self.url, data)

    def test_redirection(self):
        self.assertRedirects(self.response, self.url)

    def test_data_updated(self):
        self.user.refresh_from_db()
        self.assertEquals(self.user.first_name, self.first_name)
        self.assertEquals(self.user.last_name, self.last_name)
        self.assertEquals(self.user.email, self.new_email)


class InvalidChangesTests(MyAccountTestCase):
    def setUp(self):
        '''
        Submit an empty dictionary to the 'my_account' view
        '''
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {})

    def test_redirection(self):
        '''
        An invalid form submission should return to the same page
        '''
        self.assertRedirects(self.response, self.url)
