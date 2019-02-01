from django.test import TestCase
from django.core.urlresolvers import reverse
from django.urls import resolve
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from accounts.views import signup


# Create your tests here.
class SignUpTests(TestCase):
    def setUp(self):
        self.url = reverse('signup')
        self.response = self.client.get(self.url)

    def test_signup_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        view = resolve('/signup/')
        self.assertEquals(view.func, signup)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, UserCreationForm)

    def test_signup_post_with_valid_data(self):
        data = {
            'username': 'jean',
            'password1': 'passsentence',
            'password2': 'passsentence',
        }
        self.client.post(self.url, data)
        self.assertTrue(User.objects.exists())

    def test_signup_invalid_post_data(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation error
        '''
        response = self.client.post(self.url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_signup_invalid_post_data_empty_fields(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation error
        '''
        data = {
            'subject': '',
            'message': '',
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(User.objects.exists())
