from lib2to3.fixes.fix_input import context

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from users.forms import StudyGroupForm, RegisterUserForm, LoginForm
from users.models import StudyGroup


# Create your views here.
@login_required
def group_list(request):
    if request.method == 'POST':
        form = StudyGroupForm(data=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "Группа успешна создана")
    else:
        form = StudyGroupForm()
    groups = StudyGroup.objects.filter(is_active=True)

    return render(
        request, 'users/study_group_list.html', context={'title': 'Группы', 'groups': groups, 'form': form},
    )


@login_required
def group_detail(request, pk):
    # TODO: permission
    group = get_object_or_404(StudyGroup, pk=pk)
    if request.method == 'POST':
        form = StudyGroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save()
            messages.add_message(request, messages.SUCCESS, "Группа успешна обновлена")
    form = StudyGroupForm(instance=group)
    return render(
        request, 'users/study_group_detail.html',
        context={'title': f'Группа {group.name}', 'form': form, 'group': group},
    )


@login_required
def group_delete(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)
    group.delete()
    messages.add_message(request, messages.SUCCESS, "Группа успешна удалена")
    return redirect(reverse('users:group-list'))


class LoginUser(LoginView):
    template_name = 'users/logister.html'
    form_class = LoginForm
    extra_context = {'title': 'Авторизация'}
    success_url = 'users:group-list'


def register_user(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user = form.save()
            messages.add_message(request, messages.SUCCESS, "Пользователь успешно создан")
            return redirect(reverse('users:login'))
    else:
        form = RegisterUserForm()

    return render(request, 'users/logister.html', context={'title': 'Регистрация', 'form': form})
