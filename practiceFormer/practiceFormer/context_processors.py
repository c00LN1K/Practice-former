from django.urls import reverse_lazy


def get_mainmenu(request):
    return {
        'menu': {
            'Practices': reverse_lazy('former:practice-list'),
            'Poles': reverse_lazy('former:pole-list'),
            'Groups': reverse_lazy('users:group-list'),
        }
    }