from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

from users.models import StudyGroup


class StudyGroupCreateForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = '__all__'
        exclude = ['leader', 'is_active']


class StudyGroupUpdateForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = '__all__'
        exclude = ['is_active']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['leader'].queryset = get_user_model().objects.filter(group_id=self.instance.pk)

    def clean_leader(self):
        leader = self.cleaned_data['leader']
        if leader and leader.group != self.instance:
            raise forms.ValidationError('Старостой группы может быть только пользователь, состоящий в этой группе')
        return leader


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Придумайте логин', widget=forms.TextInput(attrs={}))
    password1 = forms.CharField(label='Придумайте пароль', widget=forms.PasswordInput(attrs={}))
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput(attrs={}))
    first_name = forms.CharField(label='Имя')

    class Meta:
        model = get_user_model()
        fields = [
            'username', 'email', 'first_name', 'second_name', 'patronymic', 'role', 'group', 'residence',
            'phone', 'password1', 'password2',
        ]
        labels = {'email': 'Email'}

    def clean(self):
        group, role = self.cleaned_data['group'], self.cleaned_data['role']
        if group and role == get_user_model().Role.TUTOR:
            raise ValidationError('У преподавателя не может быть группы!')
        return super().clean()


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']
