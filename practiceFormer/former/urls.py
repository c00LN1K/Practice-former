from django.urls import path

from former import views

app_name = 'former'

urlpatterns = [
    path('practices', views.practice_list, name='practice-list'),
    path('practices/<int:pk>', views.practice_detail, name='practice-detail'),
    path('practices/<int:pk>/delete', views.practice_destroy, name='practice-destroy'),
    path('practices/<int:pk>/admins', views.practice_admins, name='practice-admins')
]