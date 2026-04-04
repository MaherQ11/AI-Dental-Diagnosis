from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # Patient
    path('patient/register/', views.patient_register, name='patient_register'),
    path('patient/login/',    views.patient_login,    name='patient_login'),
    path('patient/logout/',   views.patient_logout,   name='patient_logout'),
    path('patient/',          views.patient_main,          name='patient_main'),
    path('patient/scan/',     views.patient_chat_with_ai,  name='patient_scan'),
    path('patient/history/',  views.patient_check_history, name='patient_history'),
    path('patient/appointment/', views.patient_appointment, name='patient_appointment'),
    path('patient/chat-doctor/', views.patient_chat_with_doctor, name='patient_chat_doctor'),
    path('patient/feedback/', views.patient_feedback,   name='patient_feedback'),
    path('patient/account/',  views.patient_account,    name='patient_account'),

    # Doctor
    path('doctor/register/',  views.doctor_register,      name='doctor_register'),
    path('doctor/login/',     views.doctor_login,          name='doctor_login'),
    path('doctor/logout/',    views.doctor_logout,         name='doctor_logout'),
    path('doctor/',           views.doctor_dashboard,      name='doctor_dashboard'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/cases/',     views.doctor_patient_cases,  name='doctor_cases'),
    path('doctor/chat/',      views.doctor_patient_chat,   name='doctor_chat'),
]
