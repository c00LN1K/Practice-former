from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from former.models import Practice
from users.models import StudyGroup


# Create your tests here.
class TestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_tutor = get_user_model().objects.create(
            username='test_tutor', first_name='Test', second_name='Tutor', role=get_user_model().Role.TUTOR,
        )
        cls.user_tutor.set_password('password')
        cls.user_tutor.save()

        cls.test_group = StudyGroup.objects.create(name='Test group', start_time=2024)
        cls.user_student = get_user_model().objects.create(
            username='test_user', first_name='Test', second_name='Student', role=get_user_model().Role.STUDENT,
            group=cls.test_group,
        )
        cls.user_student.set_password('password')
        cls.user_student.save()

    def test_create_practice(self):
        form_data = {
            'period': 'test',
            'group': self.test_group.pk,
            'director': self.user_tutor.pk,
        }

        self.assertTrue(self.client.login(username='test_tutor', password='password'))
        response = self.client.post(path=reverse('former:practice-list'), data=form_data)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Practice.objects.count(), 1)
