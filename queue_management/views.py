


from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import Max
from django.utils import timezone
from django.views.decorators.http import require_POST

from clinics.models import Clinic, Doctor
from .models import QueueToken


def doctor_list(request, clinic_id):
    clinic = get_object_or_404(
        Clinic,
        id=clinic_id,
        is_active=True
    )

    doctors = Doctor.objects.filter(
        clinic=clinic,
        is_available=True
    ).select_related('user')

    return render(request, 'queue_management/doctor_list.html', {
        'clinic': clinic,
        'doctors': doctors
    })


@login_required
def book_token(request):

    # Doctors should not book patient tokens
    if hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Doctors cannot book patient tokens.')
        return redirect('doctor_dashboard')

    clinics = Clinic.objects.filter(is_active=True)

    doctors = Doctor.objects.filter(
        is_available=True,
        clinic__is_active=True
    ).select_related('clinic', 'user')

    if request.method == 'POST':

        clinic_id = request.POST.get('clinic')
        doctor_id = request.POST.get('doctor')
        booking_date = request.POST.get('booking_date')

        clinic = get_object_or_404(
            Clinic,
            id=clinic_id,
            is_active=True
        )

        doctor = get_object_or_404(
            Doctor,
            id=doctor_id,
            clinic=clinic,
            is_available=True
        )

        try:
            selected_date = datetime.strptime(
                booking_date, '%Y-%m-%d'
            ).date()
        except (ValueError, TypeError):
            messages.error(request, 'Please select a valid date.')
            return redirect('book_token')

        if selected_date < timezone.localdate():
            messages.error(request, 'Past dates are not allowed.')
            return redirect('book_token')

        try:
            with transaction.atomic():

                last_token = QueueToken.objects.filter(
                    doctor=doctor,
                    booking_date=selected_date
                ).aggregate(
                    max_token=Max('token_number')
                )['max_token']

                next_token = (last_token or 0) + 1

                booking = QueueToken.objects.create(
                    patient=request.user,
                    clinic=clinic,
                    doctor=doctor,
                    token_number=next_token,
                    booking_date=selected_date,
                    status='WAITING'
                )

            messages.success(
                request,
                f'Booking successful! Your token number is {booking.token_number}.'
            )

            return redirect('my_bookings')

        except IntegrityError:
            messages.error(
                request,
                'Booking conflict. Please try again.'
            )
            return redirect('book_token')

    return render(request, 'queue_management/book_token.html', {
        'clinics': clinics,
        'doctors': doctors,
        'today': timezone.localdate().isoformat()
    })


@login_required
def my_bookings(request):

    # Doctors should not access patient bookings
    if hasattr(request.user, 'doctor_profile'):
        return redirect('doctor_dashboard')

    bookings = QueueToken.objects.filter(
        patient=request.user
    ).select_related(
        'clinic', 'doctor', 'doctor__user'
    ).order_by('-booking_date', '-token_number')

    return render(request, 'queue_management/my_bookings.html', {
        'bookings': bookings
    })


@login_required
@require_POST
def cancel_booking(request, token_id):

    if hasattr(request.user, 'doctor_profile'):
        return redirect('doctor_dashboard')

    booking = get_object_or_404(
        QueueToken,
        id=token_id,
        patient=request.user
    )

    if booking.status == 'WAITING':

        booking.status = 'CANCELLED'
        booking.save(update_fields=['status'])

        messages.success(
            request,
            'Booking cancelled successfully.'
        )

    else:
        messages.error(
            request,
            'Only waiting tokens can be cancelled.'
        )

    return redirect('my_bookings')


# LIVE QUEUE TRACKING

@login_required
def track_queue(request, token_id):

    if hasattr(request.user, 'doctor_profile'):
        return redirect('doctor_dashboard')

    booking = get_object_or_404(
        QueueToken.objects.select_related(
            'clinic',
            'doctor',
            'doctor__user'
        ),
        id=token_id,
        patient=request.user
    )

    queue_tokens = QueueToken.objects.filter(
        doctor=booking.doctor,
        booking_date=booking.booking_date
    )

    current_booking = queue_tokens.filter(
        status__in=['CALLED', 'IN_PROGRESS']
    ).order_by('-token_number').first()

    current_token = (
        current_booking.token_number
        if current_booking else 0
    )

    patients_ahead = queue_tokens.filter(
        token_number__lt=booking.token_number,
        status='WAITING'
    ).count()

    return render(
        request,
        'queue_management/track_queue.html',
        {
            'booking': booking,
            'current_token': current_token,
            'patients_ahead': patients_ahead,
        }
    )


# DOCTOR DASHBOARD

@login_required
def doctor_dashboard(request):

    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('home')

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    today = timezone.localdate()

    bookings = QueueToken.objects.filter(
        doctor=doctor,
        booking_date=today
    ).select_related(
        'patient',
        'clinic'
    ).order_by('token_number')

    waiting_count = bookings.filter(
        status='WAITING'
    ).count()

    completed_count = bookings.filter(
        status='COMPLETED'
    ).count()

    current_booking = bookings.filter(
        status__in=['CALLED', 'IN_PROGRESS']
    ).order_by('-token_number').first()

    return render(
        request,
        'queue_management/doctor_dashboard.html',
        {
            'doctor': doctor,
            'bookings': bookings,
            'waiting_count': waiting_count,
            'completed_count': completed_count,
            'current_booking': current_booking,
            'today': today,
        }
    )


# CALL NEXT TOKEN

@login_required
@require_POST
def call_next_token(request):

    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('home')

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    today = timezone.localdate()

    with transaction.atomic():

        # Lock the doctor record while checking and calling next token
        Doctor.objects.select_for_update().get(id=doctor.id)

        active_booking = QueueToken.objects.filter(
            doctor=doctor,
            booking_date=today,
            status__in=['CALLED', 'IN_PROGRESS']
        ).exists()

        if active_booking:
            messages.warning(
                request,
                'Please complete the current patient before calling the next token.'
            )
            return redirect('doctor_dashboard')

        next_booking = QueueToken.objects.select_for_update().filter(
            doctor=doctor,
            booking_date=today,
            status='WAITING'
        ).order_by('token_number').first()

        if next_booking:

            next_booking.status = 'CALLED'
            next_booking.called_at = timezone.now()

            next_booking.save(
                update_fields=['status', 'called_at']
            )

            messages.success(
                request,
                f'Token {next_booking.token_number} called successfully.'
            )

        else:
            messages.info(
                request,
                'No waiting patients available.'
            )

    return redirect('doctor_dashboard')


# UPDATE TOKEN STATUS

@login_required
@require_POST
def update_token_status(request, token_id, action):

    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('home')

    doctor = get_object_or_404(
        Doctor,
        user=request.user
    )

    booking = get_object_or_404(
        QueueToken,
        id=token_id,
        doctor=doctor,
        booking_date=timezone.localdate()
    )

    if action == 'start' and booking.status == 'CALLED':

        booking.status = 'IN_PROGRESS'

        booking.save(update_fields=['status'])

        messages.success(
            request,
            'Consultation started.'
        )

    elif action == 'complete' and booking.status == 'IN_PROGRESS':

        booking.status = 'COMPLETED'
        booking.completed_at = timezone.now()

        booking.save(
            update_fields=['status', 'completed_at']
        )

        messages.success(
            request,
            'Consultation completed.'
        )

    elif action == 'skip' and booking.status in ['WAITING', 'CALLED']:

        booking.status = 'SKIPPED'

        booking.save(update_fields=['status'])

        messages.success(
            request,
            'Token skipped successfully.'
        )

    else:
        messages.error(
            request,
            'Invalid action for this token.'
        )

    return redirect('doctor_dashboard')
