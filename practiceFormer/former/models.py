from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
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

    def get_absolute_url(self):
        return reverse('former:practice-detail', args=(self.pk, ))

    # Сделать валидацию на уникальные значения в admin (метод clean or save or validate)


class UserPractice(BaseModel):
    user = models.ForeignKey(
        to=get_user_model(), on_delete=models.SET_NULL, verbose_name='Студент', blank=True, null=True,
    )
    practice = models.ForeignKey(to=Practice, on_delete=models.CASCADE, verbose_name='Практика')
    data = models.JSONField()


class Pole(BaseModel):
    name = models.CharField(verbose_name='Название', max_length=30)
    author = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, verbose_name='Автор')
    # type


class PracticePole(BaseModel):
    pole = models.ForeignKey(verbose_name='Поле', to=Pole, on_delete=models.CASCADE)
    practice = models.ForeignKey(verbose_name='Практика', to=Practice, on_delete=models.CASCADE)
    is_require = models.BooleanField(default=False)
    is_editable = models.BooleanField(default=True)
    default_value = models.CharField(max_length=50)
