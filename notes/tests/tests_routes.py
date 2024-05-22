from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            # ('notes:detail', (self.note.id,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_crud_pages(self):
        users_statuses = (
            (self.owner, HTTPStatus.OK),
            (self.unknown, HTTPStatus.NOT_FOUND),
        )
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
            # 'notes:list'
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        
