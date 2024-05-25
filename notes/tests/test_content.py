from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestHomePage(TestCase):
    NOTES_COUNT = 15
    HOME_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Jhoanne')
        cls.another_author = User.objects.create(username='Mark')
        author_notes = [
            Note(
                title=f'Title{index}',
                text='Some text',
                slug=f'slug{index}',
                author=cls.author
            )
            for index in range(cls.NOTES_COUNT)
        ]
        another_author_notes = [
            Note(
                title=f'Title{index}',
                text='Some text',
                slug=f'slug{index+cls.NOTES_COUNT}',
                author=cls.another_author
            )
            for index in range(cls.NOTES_COUNT)
        ]
        Note.objects.bulk_create(author_notes + another_author_notes)

    def test_count_authors_notes(self):
        """Check count of all users notes"""
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, self.NOTES_COUNT)

    def test_only_authors_notes(self):
        """Check only this author notes"""
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        all_slugs = [note.slug for note in object_list]
        author_notes = Note.objects.filter(author=self.author)
        author_slug = [note.slug for note in author_notes]
        self.assertEqual(all_slugs, author_slug)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
