from django.urls import path

from former import views

app_name = 'former'

urlpatterns = [
    path('', views.practice_list, name='main'),
    path('practices', views.practice_list, name='practice-list'),
    path('practices/<int:pk>', views.practice_detail, name='practice-detail'),
    path('practices/<int:pk>/delete', views.practice_destroy, name='practice-destroy'),
    path('practices/<int:pk>/admin', views.practice_admin_settings, name='practice-admin'),
    path('poles', views.pole_list, name='pole-list'),
    path('poles/<int:pk>', views.pole_detail, name='pole-detail'),
    path('poles/<int:pk>', views.pole_destroy, name='pole-destroy'),
    path('practices/<int:pk>/users', views.practice_users, name='practice-users'),
    path('practices/<int:pk>/poles', views.practice_poles, name='practice-poles'),
    path('practices/<int:pk>/admins', views.practice_admins, name='practice-admins'),


    path('user-practice/<int:pk>', views.user_practice_detail, name='user-practice-detail'),

]
