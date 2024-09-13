from django.contrib.auth.views import LogoutView
from django.urls import path

from users import views

app_name = 'users'
urlpatterns = [
    path('groups/', views.group_list, name='group-list'),
    path('groups/<int:pk>', views.group_detail, name='group-detail'),
    path('groups/<int:pk>/delete', views.group_delete, name='group-destroy'),
    path('login', views.LoginUser.as_view(), name='login'),
    path('register', views.register_user, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
]