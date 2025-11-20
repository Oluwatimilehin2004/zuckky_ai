from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/chat/', views.chat_message, name='chat_message'),
    path('api/upload/', views.upload_video, name='upload_video'),
    path('api/process/', views.process_video, name='process_video'),
    path('api/status/<str:task_id>/', views.check_processing_status, name='check_status'),
]