import io
import xlsxwriter
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, F, Value, Subquery
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from former.forms import PracticeCreateForm, PracticeUpdateForm, PoleForm, PracticePolesForm, PracticeUsersForm, \
    PracticeAdminsForm, UserPracticeUpdateForm
from former.models import Practice, Pole, UserPractice, PracticePole


# Create your views here.
@login_required
def practice_list(request):
    is_tutor = get_user_model().Role.TUTOR == request.user.role
    form = PracticeCreateForm(request=request)
    practices = (
        Practice.objects
        .filter(Q(director=request.user) | Q(admins__contains=[request.user.pk]))
        .prefetch_related('group')
    )
    if is_tutor:
        if request.method == 'POST':
            form = PracticeCreateForm(request.POST, request=request)
            if form.is_valid():
                practice = form.save()
                messages.add_message(request, messages.SUCCESS, 'Практика успешно создана')
                return redirect(reverse('former:practice-admin', args=(practice.pk,)))

    else:
        practices |= Practice.objects.filter(
            pk__in=Subquery(UserPractice.objects.filter(user=request.user, is_active=True).values('practice_id')),
        ).prefetch_related('group')

    practices = practices.annotate(title=Concat(F('period'), Value(' - '), F('group__name')))
    return render(
        request, 'former/practice_list.html', context={
            'title': 'Практики', 'form': form, 'practices': practices, 'is_tutor': is_tutor,
        },
    )


@login_required
def practice_detail(request, pk):
    practice = get_object_or_404(Practice, pk=pk)
    user_practices = UserPractice.objects.filter(practice=practice, is_active=True).prefetch_related('user').order_by(
        'user__first_name', 'user__second_name')
    is_admin = request.user.pk in practice.admins or request.user == practice.director
    return render(
        request, 'former/practice_detail.html', context={
            'title': 'Практика', 'practice': practice, 'user_practices': user_practices, 'is_admin': is_admin,
        },
    )


@login_required
def practice_finish(request, pk):
    practice = get_object_or_404(Practice, pk=pk)
    if practice.director != request.user:
        return redirect(reverse('former:practice_detail', args=(practice.pk,)))
    practice.is_active = False
    practice.save()
    messages.add_message(request, messages.SUCCESS, "Практика успешна закончена")
    return redirect(reverse('former:practice-list'))


@login_required
def practice_admin_settings(request, pk):
    practice = get_object_or_404(Practice, pk=pk)
    is_admin = request.user.pk in practice.admins or request.user == practice.director
    if not is_admin:
        raise PermissionDenied()
    if request.method == 'POST':
        form = PracticeUpdateForm(request.POST, instance=practice, request=request)
        if form.is_valid():
            practice = form.save()
            messages.add_message(request, messages.SUCCESS, 'Практика успешно обновлена')
    else:
        form = PracticeUpdateForm(instance=practice, request=request)
    poles_form = PracticePolesForm(instance=practice, request=request)
    users_form = PracticeUsersForm(instance=practice, request=request)
    admins_form = None
    if practice.director == request.user:
        admins_form = PracticeAdminsForm(instance=practice, request=request)
    return render(
        request, 'former/practice_admin.html', context={
            'title': 'Администрирование практики', 'admins_form': admins_form, 'practice': practice,
            'poles_form': poles_form, 'users_form': users_form, 'form': form,
        },
    )


@login_required
def practice_users(request, pk):
    practice = get_object_or_404(Practice, pk=pk)
    is_admin = request.user.pk in practice.admins or request.user == practice.director
    if not is_admin:
        raise PermissionDenied()
    if request.method == 'POST':
        form = PracticeUsersForm(request.POST, instance=practice, request=request)
        if form.is_valid():
            form.save()
    return redirect(reverse('former:practice-admin', args=(practice.pk,)))


@login_required
def practice_poles(request, pk):
    practice = get_object_or_404(Practice, pk=pk)
    is_admin = request.user.pk in practice.admins or request.user == practice.director
    if not is_admin:
        raise PermissionDenied()
    if request.method == 'POST':
        form = PracticePolesForm(request.POST, instance=practice, request=request)
        if form.is_valid():
            form.save()
    return redirect(reverse('former:practice-admin', args=(practice.pk,)))


@login_required
def practice_admins(request, pk):
    practice = get_object_or_404(Practice, pk=pk)
    if request.user != practice.director:
        raise PermissionDenied()
    if request.method == 'POST':
        form = PracticeAdminsForm(request.POST, instance=practice, request=request)
        if form.is_valid():
            form.save()
    return redirect(reverse('former:practice-admin', args=(practice.pk,)))


@login_required
def pole_list(request):
    if request.method == 'POST':
        form = PoleForm(request.POST)
        if form.is_valid():
            pole = form.save(commit=False)
            pole.author = request.user
            pole.save()
            messages.add_message(request, messages.SUCCESS, 'Поле успешно создано')
    else:
        form = PoleForm()
    poles = Pole.objects.filter(author=request.user.pk)
    return render(
        request, 'former/pole_list.html', context={
            'title': 'Поля', 'form': form, 'poles': poles,
        },
    )


@login_required
def pole_detail(request, pk):
    pole = get_object_or_404(Pole, pk=pk)
    is_author = pole.author == request.user
    if not is_author:
        raise PermissionDenied()
    if request.method == 'POST':
        form = PoleForm(request.POST, instance=pole)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Поле успешно изменено')
    else:
        form = PoleForm(instance=pole)
    return render(
        request, 'former/pole_detail.html', context={
            'title': 'Поле', 'form': form, 'pole': pole,
        },
    )


@login_required
def pole_destroy(request, pk):
    pole = get_object_or_404(Pole, pk=pk)
    is_author = pole.author == request.user
    if not is_author:
        raise PermissionDenied()
    pole.delete()
    messages.add_message(request, messages.SUCCESS, "Поле успешно удалено")
    return redirect(reverse('former:pole-list'))


@login_required
def user_practice_detail(request, pk):
    user_practice = get_object_or_404(UserPractice, pk=pk)
    practice = user_practice.practice
    is_allowed = request.user.pk in practice.admins or request.user == practice.director or request.user == user_practice.user
    if request.method == 'POST' and is_allowed:
        form = UserPracticeUpdateForm(request.POST, instance=user_practice, request=request)
        if form.is_valid():
            form.save()
    else:
        form = UserPracticeUpdateForm(instance=user_practice, request=request, is_allowed=is_allowed)
    return render(request, 'former/user_practice_detail.html',
                  context={
                      'title': f'{user_practice.user.first_name} {user_practice.user.second_name}', 'form': form,
                      'user_practice': user_practice, 'is_allowed': is_allowed
                  })


@login_required
def export_practice(request, pk):
    practice = get_object_or_404(Practice, pk=pk)
    # is_admin = request.user.pk in practice.admins or request.user == practice.director
    user_practices = UserPractice.objects.filter(practice=practice, is_active=True).prefetch_related('user').order_by(
        'user__first_name', 'user__second_name',
    )
    headers = PracticePole.objects.filter(practice=practice, is_active=True).select_related('pole').values_list(
        'pole__name', flat=True,
    )

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Sheet1')
    worksheet.write(0, 0, 'User')
    for col, header in enumerate(headers, 1):
        worksheet.write(0, col, header)
        worksheet.set_column(0, col, 15)

    for row, user_practice in enumerate(user_practices, 1):
        data = user_practice.data
        worksheet.write(row, 0, f'{user_practice.user.first_name} {user_practice.user.second_name}')
        for col, header in enumerate(headers, 1):
            worksheet.write(row, col, data.get(header, ''))

    workbook.close()
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="report_{practice.group.name}_{practice.period}.xlsx"'
    return response
