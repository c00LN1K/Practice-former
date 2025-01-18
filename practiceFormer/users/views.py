from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from users.forms import StudyGroupUpdateForm, RegisterUserForm, LoginForm, StudyGroupCreateForm
from users.models import StudyGroup


# Create your views here.
@login_required
def group_list(request):
    is_tutor = request.user.role == get_user_model().Role.TUTOR
    form = None
    if is_tutor:
        if request.method == 'POST':
            form = StudyGroupCreateForm(data=request.POST)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS, "Группа успешна создана")
        else:
            form = StudyGroupCreateForm()
    groups = StudyGroup.objects.filter(is_active=True)

    return render(
        request, 'users/study_group_list.html', context={'title': 'Группы', 'groups': groups, 'form': form},
    )


@login_required
def group_detail(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)
    form = None
    tutor = get_user_model().Role.TUTOR
    if request.user.role == tutor or group.leader == request.user:
        form = StudyGroupUpdateForm(instance=group)
        if request.method == 'POST':
            form = StudyGroupUpdateForm(request.POST, instance=group)
            if form.is_valid():
                group = form.save()
                messages.add_message(request, messages.SUCCESS, "Группа успешна обновлена")
    users = get_user_model().objects.filter(group=group)
    return render(
        request, 'users/study_group_detail.html',
        context={'title': f'Группа {group.name}', 'form': form, 'group': group, 'users': users, 'tutor': tutor},
    )


@login_required
def group_achieve(request, pk):
    group = get_object_or_404(StudyGroup, pk=pk)
    if request.user != get_user_model().Role.TUTOR or group.leader != request.user:
        return redirect(reverse('users:group-detail', args=(group.pk,)))
    group.is_active = False
    group.save()
    messages.add_message(request, messages.SUCCESS, "Группа успешна заархивирована")
    return redirect(reverse('users:group-list'))


class LoginUser(LoginView):
    template_name = 'users/logister.html'
    form_class = LoginForm
    extra_context = {'title': 'Авторизация'}
    success_url = 'users:group-list'


def register_user(request):
    if request.user.is_authenticated:
        return redirect(reverse('users:login'))
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            form.save()
            messages.add_message(request, messages.SUCCESS, "Пользователь успешно создан")
            return redirect(reverse('users:login'))
    else:
        form = RegisterUserForm()

    return render(request, 'users/register.html',
                  context={'title': 'Регистрация', 'form': form, 'tutor': get_user_model().Role.TUTOR})
