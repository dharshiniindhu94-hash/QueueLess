
from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Admin Dashboard
    path(
        'admin-dashboard/',
        admin_views.admin_dashboard,
        name='admin_dashboard'
    ),
    # Patient Management
    path( 
        'admin-dashboard/patients/',
        admin_views.patient_admin_list,
        name='patient_admin_list'
    ),
    # Admin Booking Management
    path(
        'admin-dashboard/bookings/',
        admin_views.booking_admin_list,
        name='booking_admin_list'
    ),
]
