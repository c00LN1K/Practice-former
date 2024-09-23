from django.contrib import admin

from users.models import StudyGroup, User

# Register your models here.
admin.site.register(StudyGroup)
admin.site.register(User)
