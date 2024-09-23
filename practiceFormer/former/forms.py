from bisect import insort

from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q

from former.models import Practice, Pole, UserPractice, PracticePole
from users.models import User


class PracticeCreateForm(forms.ModelForm):
    poles = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, required=False,
        queryset=Pole.objects.none(), label='Поля',
    )

    class Meta:
        model = Practice
        fields = ['period', 'group', 'director', 'additional']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['director'].queryset = get_user_model().objects.filter(role=get_user_model().Role.TUTOR)
        self.fields['poles'].queryset = Pole.objects.filter(
            Q(type=Pole.PoleType.SYSTEM) | Q(author=getattr(self.request, 'user', None))
        )
        if not self.fields['poles'].queryset:
            self.fields['poles'].label = ''

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.admins = [instance.director.pk]
        instance = super().save(commit=commit)
        poles = self.cleaned_data['poles']
        if poles:
            practice_poles = []
            for pole in poles:
                practice_poles.append(PracticePole(pole=pole, practice=instance))
            PracticePole.objects.bulk_create(practice_poles)
        users = get_user_model().objects.filter(group=instance.group)
        if users:
            practice_users = []
            for user in users:
                practice_users.append(UserPractice(practice=instance, user=user))
            UserPractice.objects.bulk_create(practice_users)
        return instance


class PracticeUpdateForm(forms.ModelForm):
    class Meta:
        model = Practice
        fields = ['period', 'group', 'director', 'additional']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['director'].queryset = get_user_model().objects.filter(role=get_user_model().Role.TUTOR)
        # if getattr(self.request, 'user', None) != getattr(self.instance, 'director', None):
        #     self.fields['admins'].widget.attrs['disabled'] = 'disabled'
        #     self.fields['admins'].label = ''
        # else:
        #     self.fields['admins'].queryset = get_user_model().objects.filter(
        #         Q(group=getattr(self.instance, 'group', None)) | Q(role=get_user_model().Role.TUTOR),
        #     )
        #     self.fields['admins'].initial = getattr(self.instance, 'admins', None)

    def clean_group(self):
        group = self.cleaned_data.get('group')
        if 'group' in getattr(self.request, 'POST', None):
            if getattr(self.instance, 'group', None) != group:
                raise forms.ValidationError('Изменение группы запрещено')
        return group

    def clean_director(self):
        director = self.cleaned_data.get('director')
        if getattr(self.instance, 'director', None) != director:
            if getattr(self.instance, 'director', None) != getattr(self.request, 'user', None):
                raise forms.ValidationError('Только руководитель может редактировать это поле')
        if director.role != User.Role.TUTOR:
            raise forms.ValidationError('Руководителем может быть только преподаватель')
        return director

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.director not in instance.admins:
            instance.admins.append(instance.director.pk)
        instance = super().save(commit=commit)
        return instance


class PracticeUsersForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, required=False,
        queryset=get_user_model().objects.none(), label='Пользователи',
    )

    class Meta:
        model = Practice
        fields = []

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['users'].queryset = get_user_model().objects.filter(group=getattr(self.instance, 'group', None))
        self.fields['users'].initial = (
            UserPractice.objects.filter(practice=self.instance, is_active=True).values_list('user_id', flat=True)
        )

    def save(self, commit=True):
        instance = super().save(commit=commit)
        users = self.cleaned_data['users']
        UserPractice.objects.filter(practice=instance).update(is_active=False)
        if users:
            UserPractice.objects.filter(practice=instance, user__in=users).update(is_active=True)
        return instance


class PracticePolesForm(forms.ModelForm):
    poles = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, required=False,
        queryset=Pole.objects.none(), label='Поля',
    )

    class Meta:
        model = Practice
        fields = []

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['poles'].queryset = Pole.objects.filter(
            Q(type=Pole.PoleType.SYSTEM) | Q(author=getattr(self.request, 'user', None))
        )
        self.fields['poles'].initial = (
            PracticePole.objects.filter(practice=self.instance, is_active=True).values_list('pole_id', flat=True)
        )

    def save(self, commit=True):
        instance = super().save(commit=commit)
        poles = self.cleaned_data['poles']
        PracticePole.objects.filter(practice=instance).update(is_active=False)
        PracticePole.objects.filter(practice=instance, pole__in=poles).update(is_active=True)
        practice_poles = {
            practice_pole.pole: practice_pole
            for practice_pole in PracticePole.objects.filter(practice=instance, is_active=True).select_related('pole')
        }
        create_objs = []
        for pole in poles:
            if pole not in practice_poles:
                create_objs.append(PracticePole(pole=pole, practice=instance))
        PracticePole.objects.bulk_create(create_objs)
        return instance


class PracticeAdminsForm(forms.ModelForm):
    admins = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False, label='Администраторы',
    )

    class Meta:
        model = Practice
        fields = []

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # TODO: Fix getting leader
        self.fields['admins'].queryset = get_user_model().objects.filter(
            Q(role=get_user_model().Role.TUTOR) | Q(group_leader=getattr(self.instance, 'group', -1)))
        self.fields['admins'].initial = getattr(self.instance, 'admins', None)

    def save(self, commit=True):
        instance = super().save(commit=False)
        admins = list(self.cleaned_data['admins'].values_list('pk', flat=True))
        if admins:
            if instance.director.pk not in admins:
                admins.append(instance.director.pk)
            instance.admins = admins
        instance = super().save(commit=commit)
        return instance


class UserPracticeUpdateForm(forms.ModelForm):
    class Meta:
        model = UserPractice
        fields = []

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        data = getattr(self.instance, 'data', None)
        practice = getattr(self.instance, 'practice', None)
        fields = PracticePole.objects.filter(practice=practice, is_active=True).select_related('pole').values_list('pole__name', flat=True)
        for field in fields:
            self.fields[field] = forms.CharField(
                label=field,
                max_length=100,
                required=False,
            )
            self.fields[field].initial = data.get(field, '')

    def save(self, commit=True):
        practice = getattr(self.instance, 'practice_id', None)
        fields = PracticePole.objects.filter(practice=practice, is_active=True).select_related('pole').values_list('pole__name', flat=True)
        self.instance.data.update(
            {field: self.cleaned_data[field] for field in fields if field in self.cleaned_data}
        )
        instance = super().save(commit=commit)
        return instance


class PoleForm(forms.ModelForm):
    class Meta:
        model = Pole
        fields = ['name']
