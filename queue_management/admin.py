from django.contrib import admin
from .models import QueueToken


@admin.register(QueueToken)
class QueueTokenAdmin(admin.ModelAdmin):

    list_display = (
        'token_number',
        'patient',
        'clinic',
        'doctor',
        'booking_date',
        'status',
    )

    list_filter = (
        'status',
        'booking_date',
        'clinic',
    )

    search_fields = (
        'patient__username',
        'doctor__user__username',
    )

    ordering = ('booking_date', 'token_number')