from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('upload/', views.upload_document, name='upload_document'),
    path('process-document/', views.process_document, name='process_document'),
    path('validate-text/', views.validate_text, name='validate_text'),
    path('ask/', views.ask_question, name='ask_question'),
    
    # New reminder endpoints
    path('reminders/create/', views.create_reminder, name='create_reminder'),
    path('reminders/list/', views.get_reminders, name='get_reminders'),
    path('reminders/<int:reminder_id>/status/', views.update_reminder_status, name='update_reminder_status'),
    path('process-reminders/', views.process_reminders, name='process_reminders'),
    
    # Legacy endpoint (deprecated)
    path('schedule/', views.schedule_appointment, name='schedule_appointment'),
] 