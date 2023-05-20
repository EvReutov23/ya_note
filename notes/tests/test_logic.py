from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import Client, TestCase
from notes.models import Note

User = get_user_model()


class TestNotesCreation(TestCase):
    SLUG_TEXT = 'slug'
    NOTE_TEXT = 'Запись'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Синий Трактор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse('notes:add')
        cls.url_done = reverse('notes:success')
        cls.form_data = {
            'title': 'Заголовок', 'text': cls.NOTE_TEXT, 'slug': cls.SLUG_TEXT,
        }

    def test_anonymous_user_cant_create_notes(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_notes(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, '/done/')
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.SLUG_TEXT)
        self.assertEqual(note.author, self.user)


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст'
    NEW_NOTE_TEXT = 'Обновлённый текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор записи')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Автор другой записи')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       slug='slug', author=cls.author)
        note_slug = cls.note.slug
        cls.url = reverse('notes:detail', args=(note_slug,))
        cls.edit_url = reverse('notes:edit', args=(note_slug,))
        cls.delete_url = reverse('notes:delete', args=(note_slug,))

        cls.form_data = {'text': cls.NEW_NOTE_TEXT}

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, '/done/')
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertEquals(response.status_code, HTTPStatus.OK)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
