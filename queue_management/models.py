from django.db import models
from django.conf import settings
from clinics.models import Clinic, Doctor


class QueueToken(models.Model):

    STATUS_CHOICES = [
        ('WAITING', 'Waiting'),
        ('CALLED', 'Called'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('SKIPPED', 'Skipped'),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='queue_tokens'
    )

    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE
    )

    token_number = models.PositiveIntegerField()

    booking_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='WAITING'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    called_at = models.DateTimeField(
        null=True,
        blank=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'doctor',
                    'booking_date',
                    'token_number'
                ],
                name='unique_doctor_daily_token'
            )
        ]

    def __str__(self):
        return f"Token {self.token_number}"
