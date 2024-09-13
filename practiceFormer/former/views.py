from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from former.forms import PracticeForm
from former.models import Practice


# Create your views here.
@login_required
def practice_list(request):
    if request.method  == 'POST':
        form = PracticeForm(request.POST)
        if form.is_valid():
            practice = form.save(commit=False)
            practice.admins = list({request.user.pk, practice.director.pk})
            practice.save()
            messages.add_message(request, messages.SUCCESS, 'Практика успешно создана')
    else:
        form = PracticeForm()
    practices = Practice.objects.filter(Q(director=request.user) | Q(admins__contains=[request.user.pk]))
    return render(
        request, 'former/practice_list.html', context={'title': 'Практики', 'form': form, 'practices': practices},
    )

@login_required
def practice_detail(request, pk):
    practice = get_object_or_404(Practice, pk=pk)
    if request.method == 'POST':
        form = PracticeForm(request.POST, instance=practice)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Практика успешно изменена')
    else:
        form = PracticeForm(instance=practice)
    return render(
        request, 'former/practice_detail.html',
        context={'title': 'Практика', 'form': form, 'practice': practice},
    )


@login_required
def practice_destroy(request, pk):
    practice = get_object_or_404(Practice, pk=pk)
    practice.delete()
    messages.add_message(request, messages.SUCCESS, "Практика успешна удалена")
    return redirect(reverse('former:practice-list'))

@login_required
def practice_admins(request, pk):
    practice = get_object_or_404(Practice, pk=pk)
    admins = get_user_model().objects.filter(pk__in=practice.admins)

    return render(
        request, 'former/edit_practice_admins.html', context={'title':'Изменить админов', 'admins':admins, 'practice':practice},
    )