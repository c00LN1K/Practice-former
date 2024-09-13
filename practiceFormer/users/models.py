

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from practiceFormer.models import BaseModel


# Create your models here.

class User(AbstractUser, BaseModel):
    class Role(models.IntegerChoices):
        STUDENT = 0, 'Студент'
        TUTOR = 1, 'Преподаватель'

    second_name = models.CharField(verbose_name='Фамилия', max_length=20)
    patronymic = models.CharField(verbose_name='Отчество', blank=True, max_length=20)
    group = models.ForeignKey(verbose_name='Группа', to='StudyGroup', on_delete=models.CASCADE, related_name='users', blank=True, null=True)
    residence = models.CharField(verbose_name='Место жительства', max_length=50, blank=True)
    phone = models.CharField(verbose_name='Номер телефона', max_length=12, blank=True)
    role = models.IntegerField(verbose_name='Должность', choices=Role.choices, default=Role.STUDENT)

class StudyGroup(BaseModel):
    name = models.CharField(verbose_name='Название')
    leader = models.ForeignKey(verbose_name='Староста', to=User, on_delete=models.SET_NULL, blank=True, null=True, max_length=50)
    faculty = models.CharField(verbose_name='Факультет', max_length=50, blank=True)
    subject = models.CharField(verbose_name='Направление', blank=True, max_length=50)
    start_time = models.PositiveIntegerField(verbose_name='Год поступления', blank=True)
    is_active = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('users:group-detail', args=(self.pk,))