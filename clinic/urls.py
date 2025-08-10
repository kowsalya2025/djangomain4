from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'clinic'

urlpatterns = [
    path('', views.doctors_list, name='doctors_list'),
    path('doctor/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('doctor/<int:doctor_id>/book/', views.book_appointment, name='book_appointment'),
    path('appointments/', views.my_appointments, name='my_appointments'),
    path('appointment/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointment/<int:appointment_id>/prescription/', views.prescription_create, name='prescription_create'),
    path('tests/upload/', views.upload_test_result, name='upload_test_result'),
    path('reports/daily/', views.daily_report, name='daily_report'),
    # auth
    path('login/', auth_views.LoginView.as_view(template_name='clinic/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='clinic:doctors_list'), name='logout'),
]