from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    title, text, slug = 'title', 'text', 'slug0'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Anna')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': cls.title,
            'text': cls.text,
            'slug': cls.slug
        }

    def test_anonymous_user_cant_create_note(self):
        login_url = reverse('users:login')
        response = self.client.post(self.url, data=self.form_data)
        redirect_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, redirect_url)
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.title)
        self.assertEqual(note.text, self.text)
        self.assertEqual(note.slug, self.slug)
        self.assertEqual(note.author, self.user)

    def test_user_cant_use_same_slug(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.slug + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(expected_slug, new_note.slug)


class TestNoteEditDelete(TestCase):
    title, text, slug, new = 'title', 'text', 'slug0', 'new'

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create(username='Elsa')
        cls.owner_client = Client()
        cls.owner_client.force_login(cls.owner)

        cls.not_owner = User.objects.create(username='Olaf')
        cls.not_owner_client = Client()
        cls.not_owner_client.force_login(cls.not_owner)

        cls.note = Note.objects.create(
            title=cls.title,
            text=cls.text,
            slug=cls.slug,
            author=cls.owner
        )

        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.title + cls.new,
            'text': cls.text + cls.new,
            'slug': cls.slug + cls.new
        }

    def test_owner_can_delete_note(self):
        response = self.owner_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_not_owner_cant_delete_note_of_owner(self):
        response = self.not_owner_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_owner_can_edit_note(self):
        response = self.owner_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.text + self.new)
        self.assertEqual(self.note.title, self.title + self.new)
        self.assertEqual(self.note.slug, self.slug + self.new)

    def test_not_owner_cant_edit_note_of_owner(self):
        response = self.not_owner_client.post(self.edit_url,
                                              data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.text)
        self.assertEqual(self.note.title, self.title)
        self.assertEqual(self.note.slug, self.slug)
