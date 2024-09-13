from django import forms

from former.models import Practice


class PracticeForm(forms.ModelForm):
    class Meta:
        model = Practice
        fields = ['period', 'group', 'director', 'additional']
