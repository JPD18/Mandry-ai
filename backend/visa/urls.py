from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('upload/', views.upload_document, name='upload_document'),
    path('ask/', views.ask_question, name='ask_question'),
    path('schedule/', views.schedule_appointment, name='schedule_appointment'),
] 