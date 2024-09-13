from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from users.models import StudyGroup


class StudyGroupForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = '__all__'

class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Придумайте логин', widget=forms.TextInput(attrs={}))
    password1 = forms.CharField(label='Придумайте пароль', widget=forms.PasswordInput(attrs={}))
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput(attrs={}))
    first_name = forms.CharField(label='Имя')

    class Meta:
        model = get_user_model()
        fields = [
            'username', 'email', 'first_name', 'second_name', 'patronymic', 'group', 'residence',
            'phone', 'role','password1', 'password2',
        ]
        labels = {'email': 'Email'}

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


# 1. Исследование устойчивости интерполяционного полинома
# 2. Исследование фильтрующих свойств МНК