from django.db import models
from django.conf import settings

class Clinic(models.Model):

    clinic_name = models.CharField(max_length=150)

    address = models.TextField()

    contact_number = models.CharField(
        max_length=15
    )

    opening_time = models.TimeField()

    closing_time = models.TimeField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.clinic_name


class Doctor(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )

    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='doctors'
    )

    specialization = models.CharField(
        max_length=100
    )

    average_consultation_minutes = models.PositiveIntegerField(
        default=10
    )

    is_available = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.user.username
