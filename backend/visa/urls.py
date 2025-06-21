from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('process-document/', views.process_document, name='process_document'),
    path('validate-text/', views.validate_text, name='validate_text'),
    path('ask/', views.ask_question, name='ask_question'),
    path('schedule/', views.schedule_appointment, name='schedule_appointment'),
] 