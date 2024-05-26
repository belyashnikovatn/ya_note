from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create(username='Leya')
        cls.unknown = User.objects.create(username='Darth')
        cls.note = Note.objects.create(
            title='Name',
            text='Text',
            slug='slug1',
            author=cls.owner,
        )

    def test_pages_availability_for_anonymous_user(self):
        urls = (
            (''),
            ('/auth/login/'),
            ('/auth/logout/'),
            ('/auth/signup/'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = name
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            ('/notes', ''),
            ('/add', ''),
            ('/done', ''),
            ('/note/', self.note.slug),
            ('/edit/', self.note.slug),
            ('/delete/', self.note.slug),
        )
        self.client.force_login(self.owner)
        for name, args in urls:
            with self.subTest(name=name):
                url = name + args + '/'
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        urls = (
            ('/note/', self.note.slug),
            ('/edit/', self.note.slug),
            ('/delete/', self.note.slug),
        )
        users_statuses = (
            (self.owner, HTTPStatus.OK),
            (self.unknown, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = name + args + '/'
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect(self):
        urls = (
            ('/notes', ''),
            ('/add', ''),
            ('/done', ''),
            ('/note/', self.note.slug),
            ('/edit/', self.note.slug),
            ('/delete/', self.note.slug),
        )
        login_url = '/auth/login/'
        for name, args in urls:
            with self.subTest(name=name):
                url = name + args + '/'
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
