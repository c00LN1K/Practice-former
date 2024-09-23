from django.contrib import admin

from former.models import Practice, Pole, PracticePole, UserPractice

# Register your models here.
admin.site.register(Practice)
admin.site.register(Pole)
admin.site.register(PracticePole)
admin.site.register(UserPractice)
