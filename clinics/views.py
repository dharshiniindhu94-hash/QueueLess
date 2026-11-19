

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden

from .models import Clinic, Doctor
from .forms import ClinicForm, DoctorForm, DoctorEditForm

User = get_user_model()


# Patient clinic listing
def clinic_list(request):
    clinics = Clinic.objects.filter(is_active=True)

    return render(request, 'clinics/clinic_list.html', {
        'clinics': clinics
    })


# Patient clinic details
def clinic_detail(request, clinic_id):
    clinic = get_object_or_404(
        Clinic,
        id=clinic_id,
        is_active=True
    )

    doctors = Doctor.objects.filter(
        clinic=clinic,
        is_available=True
    ).select_related('user')

    return render(request, 'clinics/clinic_detail.html', {
        'clinic': clinic,
        'doctors': doctors
    })


# Admin permission check
def is_admin_user(user):
    return user.is_authenticated and user.is_superuser


@login_required
def clinic_admin_list(request):
    if not is_admin_user(request.user):
        return HttpResponseForbidden('Access denied.')

    clinics = Clinic.objects.all().order_by('-created_at')

    return render(
        request,
        'clinics/admin_clinic_list.html',
        {'clinics': clinics}
    )


@login_required
def clinic_create(request):
    if not is_admin_user(request.user):
        return HttpResponseForbidden('Access denied.')

    if request.method == 'POST':
        form = ClinicForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Clinic added successfully!')
            return redirect('clinic_admin_list')
    else:
        form = ClinicForm()

    return render(
        request,
        'clinics/clinic_form.html',
        {'form': form, 'title': 'Add Clinic'}
    )


@login_required
def clinic_update(request, clinic_id):
    if not is_admin_user(request.user):
        return HttpResponseForbidden('Access denied.')

    clinic = get_object_or_404(Clinic, id=clinic_id)

    if request.method == 'POST':
        form = ClinicForm(request.POST, instance=clinic)

        if form.is_valid():
            form.save()
            messages.success(request, 'Clinic updated successfully!')
            return redirect('clinic_admin_list')
    else:
        form = ClinicForm(instance=clinic)

    return render(
        request,
        'clinics/clinic_form.html',
        {'form': form, 'title': 'Edit Clinic'}
    )


@login_required
@require_POST
def clinic_toggle_status(request, clinic_id):
    if not is_admin_user(request.user):
        return HttpResponseForbidden('Access denied.')

    clinic = get_object_or_404(Clinic, id=clinic_id)

    clinic.is_active = not clinic.is_active
    clinic.save(update_fields=['is_active'])

    messages.success(
        request,
        'Clinic status updated successfully!'
    )

    return redirect('clinic_admin_list')


# Doctor Management - Add Doctor
@login_required
def doctor_create(request):
    if not is_admin_user(request.user):
        return HttpResponseForbidden('Access denied.')

    if request.method == 'POST':
        form = DoctorForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():

                    user = User(
                        username=form.cleaned_data['username'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        email=form.cleaned_data['email'],
                        phone_number=form.cleaned_data['phone_number'],
                        role='DOCTOR',
                        is_staff=False,
                    )

                    user.set_password(
                        form.cleaned_data['password']
                    )

                    user.save()

                    Doctor.objects.create(
                        user=user,
                        clinic=form.cleaned_data['clinic'],
                        specialization=form.cleaned_data['specialization'],
                        average_consultation_minutes=form.cleaned_data[
                            'average_consultation_minutes'
                        ],
                    )

                messages.success(
                    request,
                    'Doctor added successfully!'
                )

                return redirect('clinic_admin_list')

            except Exception:
                messages.error(
                    request,
                    'Unable to create doctor. Please try again.'
                )

    else:
        form = DoctorForm()

    return render(
        request,
        'clinics/doctor_form.html',
        {
            'form': form,
            'title': 'Add Doctor'
        }
    )
# Doctor Management - Doctor List
@login_required
def doctor_admin_list(request):

    if not is_admin_user(request.user):
        return HttpResponseForbidden('Access denied.')

    doctors = Doctor.objects.select_related(
        'user', 'clinic'
    ).all().order_by('user__username')

    return render(
        request,
        'clinics/admin_doctor_list.html',
        {'doctors': doctors}
    )

# Doctor Management - Edit Doctor
@login_required
def doctor_update(request, doctor_id):

    if not is_admin_user(request.user):
        return HttpResponseForbidden('Access denied.')

    doctor = get_object_or_404(
        Doctor.objects.select_related('user'),
        id=doctor_id
    )

    if request.method == 'POST':
        form = DoctorEditForm(request.POST)

        if form.is_valid():
            doctor.user.first_name = form.cleaned_data['first_name']
            doctor.user.last_name = form.cleaned_data['last_name']
            doctor.user.email = form.cleaned_data['email']
            doctor.user.phone_number = form.cleaned_data['phone_number']
            doctor.user.save()

            doctor.specialization = form.cleaned_data['specialization']
            doctor.clinic = form.cleaned_data['clinic']
            doctor.average_consultation_minutes = form.cleaned_data[
                'average_consultation_minutes'
            ]
            doctor.save()

            messages.success(request, 'Doctor updated successfully!')
            return redirect('doctor_admin_list')

    else:
        form = DoctorEditForm(initial={
            'first_name': doctor.user.first_name,
            'last_name': doctor.user.last_name,
            'email': doctor.user.email,
            'phone_number': doctor.user.phone_number,
            'specialization': doctor.specialization,
            'clinic': doctor.clinic,
            'average_consultation_minutes': doctor.average_consultation_minutes,
        })

    return render(
        request,
        'clinics/doctor_form.html',
        {
            'form': form,
            'title': 'Edit Doctor'
        }
    )

# Doctor Management - Activate / Deactivate
@login_required
@require_POST
def doctor_toggle_status(request, doctor_id):

    if not is_admin_user(request.user):
        return HttpResponseForbidden('Access denied.')

    doctor = get_object_or_404(Doctor, id=doctor_id)

    doctor.is_available = not doctor.is_available
    doctor.save(update_fields=['is_available'])

    if doctor.is_available:
        messages.success(request, 'Doctor activated successfully!')
    else:
        messages.success(request, 'Doctor deactivated successfully!')

    return redirect('doctor_admin_list')
