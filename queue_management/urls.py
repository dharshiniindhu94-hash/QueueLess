
from django.urls import path
from . import views

urlpatterns = [
    path(
        'clinic/<int:clinic_id>/doctors/',
        views.doctor_list,
        name='doctor_list'
    ),

    path(
        'book/',
        views.book_token,
        name='book_token'
    ),

    path(
        'my-bookings/',
        views.my_bookings,
        name='my_bookings'
    ),

    path(
        'cancel/<int:token_id>/',
        views.cancel_booking,
        name='cancel_booking'
    ),

    path(
        'track/<int:token_id>/',
        views.track_queue,
        name='track_queue'
    ),

    path(
        'doctor-dashboard/',
        views.doctor_dashboard,
        name='doctor_dashboard'
    ),

    path(
        'call-next/',
         views.call_next_token,
         name='call_next_token'
    ),

    path(
        'update-token/<int:token_id>/<str:action>/',
        views.update_token_status,
        name='update_token_status'
    ),

]
