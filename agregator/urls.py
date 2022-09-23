from django.urls import path,re_path

from . import views


appname='agregator'
urlpatterns = [
    path('', views.agg, name='agregator'),
    path('files', views.files, name='files'),
    path('task', views.task, name='task'),
    path('history', views.history, name='history'),
    path('history_keys', views.history_keys, name='history_keys'),
    path('download/<pk>/<type>/', views.download, name='download'),
    path('delete/<pk>/', views.delete, name='delete'),
    path('delete_keys/<pk>/', views.delete_keys, name='delete_keys'),
    path('restart',views.restart, name='restart'),
]
