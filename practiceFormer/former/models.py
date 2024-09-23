from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import IntegerChoices, BooleanField
from django.urls import reverse

from practiceFormer.models import BaseModel
from users.models import StudyGroup


# Create your models here.
class Practice(BaseModel):
    period = models.CharField(verbose_name='Период практики', max_length=30)
    group = models.ForeignKey(to=StudyGroup, on_delete=models.CASCADE, verbose_name='Группа')
    director = models.ForeignKey(
        to=get_user_model(), on_delete=models.DO_NOTHING, verbose_name='Руководитель'
    )
    additional = models.TextField(verbose_name='Дополнительная информация', blank=True)
    admins = ArrayField(base_field=models.BigIntegerField())
    is_active = BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('former:practice-detail', args=(self.pk,))

    # Сделать валидацию на уникальные значения в admin (метод clean or save or validate)


class UserPractice(BaseModel):
    user = models.ForeignKey(
        to=get_user_model(), on_delete=models.SET_NULL, verbose_name='Студент', blank=True, null=True,
    )
    practice = models.ForeignKey(to=Practice, on_delete=models.CASCADE, verbose_name='Практика')
    data = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('former:user-practice-detail', args=(self.pk,))


class Pole(BaseModel):
    class PoleType(IntegerChoices):
        SYSTEM = 0, 'SYSTEM'
        CUSTOM = 1, 'CUSTOM'

    name = models.CharField(verbose_name='Название', max_length=30)
    author = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, verbose_name='Автор')
    type = models.IntegerField(choices=PoleType.choices, default=PoleType.CUSTOM)

    def get_absolute_url(self):
        return reverse('former:pole-detail', args=(self.pk,))

    def __str__(self):
        return f'{self.name}'


class PracticePole(BaseModel):
    pole = models.ForeignKey(verbose_name='Поле', to=Pole, on_delete=models.CASCADE)
    practice = models.ForeignKey(verbose_name='Практика', to=Practice, on_delete=models.CASCADE)
    is_require = models.BooleanField(default=False)
    is_editable = models.BooleanField(default=True)
    default_value = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
