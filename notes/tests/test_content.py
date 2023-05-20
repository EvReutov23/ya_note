from django.shortcuts import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from notes.models import Note


User = get_user_model()


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Синий Трактор')
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       slug='slug', author=cls.author)
        cls.detail_url = reverse('notes:add')

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)

    def test_anonymous_client_has_no_form(self):
        login_url = reverse('users:login')
        response = self.client.get(self.detail_url)
        self.assertRedirects(response, f'{login_url}?next=/add/')
