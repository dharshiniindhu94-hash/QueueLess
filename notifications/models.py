from django.db import models
from django.conf import settings


class Notification(models.Model):

    NOTIFICATION_TYPES = [
        ('BOOKING', 'Booking Confirmation'),
        ('QUEUE', 'Queue Update'),
        ('TURN', 'Your Turn'),
        ('CANCEL', 'Cancellation'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.notification_type
