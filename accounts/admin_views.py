
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.http import HttpResponseForbidden

from clinics.models import Clinic, Doctor
from queue_management.models import QueueToken


User = get_user_model()


@login_required
def admin_dashboard(request):

    # Admin permission protection
    if not request.user.is_superuser:
       return HttpResponseForbidden(
        "You are not authorized to access this page."
    )

    # Dashboard statistics
    total_patients = User.objects.filter(
        role='PATIENT'
    ).count()

    total_doctors = Doctor.objects.count()

    total_clinics = Clinic.objects.count()

    total_bookings = QueueToken.objects.count()

    waiting_tokens = QueueToken.objects.filter(
        status='WAITING'
    ).count()

    completed_tokens = QueueToken.objects.filter(
        status='COMPLETED'
    ).count()

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_clinics': total_clinics,
        'total_bookings': total_bookings,
        'waiting_tokens': waiting_tokens,
        'completed_tokens': completed_tokens,
    }

    return render(
        request,
        'accounts/admin_dashboard.html',
        context
    )

# Admin - Patient Management
@login_required
def patient_admin_list(request):

    if not request.user.is_superuser:
        return HttpResponseForbidden(
            "You are not authorized to access this page."
        )

    patients = User.objects.filter(
        role='PATIENT'
    ).order_by('username')

    return render(
        request,
        'accounts/admin_patient_list.html',
        {'patients': patients}
    )

# Admin - Booking Management
@login_required
def booking_admin_list(request):

    if not request.user.is_superuser:
        return HttpResponseForbidden(
            "You are not authorized to access this page."
        )

    bookings = QueueToken.objects.select_related(
        'patient',
        'clinic',
        'doctor__user'
    ).all().order_by('-booking_date', 'token_number')

    return render(
        request,
        'accounts/admin_booking_list.html',
        {'bookings': bookings}
    )


