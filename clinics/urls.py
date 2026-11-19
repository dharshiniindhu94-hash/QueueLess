


from django.urls import path
from . import views

urlpatterns = [
    path('', views.clinic_list, name='clinic_list'),
    path('<int:clinic_id>/', views.clinic_detail, name='clinic_detail'),

    # Clinic Management
    path('admin/', views.clinic_admin_list, name='clinic_admin_list'),
    path('admin/add/', views.clinic_create, name='clinic_create'),
    path('admin/edit/<int:clinic_id>/', views.clinic_update, name='clinic_update'),
    path('admin/toggle/<int:clinic_id>/', views.clinic_toggle_status, name='clinic_toggle_status'),

    # Doctor Management
    path('admin/doctors/', views.doctor_admin_list, name='doctor_admin_list'),
    path('admin/doctors/add/', views.doctor_create, name='doctor_create'),
    path('admin/doctors/edit/<int:doctor_id>/',views.doctor_update,name='doctor_update'),
    path('admin/doctors/toggle/<int:doctor_id>/',views.doctor_toggle_status, name='doctor_toggle_status'),
]
