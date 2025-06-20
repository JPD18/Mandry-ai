from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_document, name='upload_document'),
    path('ask/', views.ask_question, name='ask_question'),
    path('schedule/', views.schedule_appointment, name='schedule_appointment'),
] 