from django.conf import settings
from django.db import models

from apps.properties.models import Property


class InterestRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    )
    REJECTION_REASON_UNAVAILABLE = 'property_unavailable'
    REJECTION_REASON_PAYMENT_TERMS = 'payment_terms_not_compatible'
    REJECTION_REASON_RENTAL_PERIOD = 'rental_period_too_short'

    REJECTION_REASON_CHOICES = (
        (REJECTION_REASON_UNAVAILABLE, 'Property is no longer available'),
        (REJECTION_REASON_PAYMENT_TERMS, 'Payment terms are not compatible'),
        (REJECTION_REASON_RENTAL_PERIOD, 'Rental period is too short'),
    )

    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_interest_requests',
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='interest_requests',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_interest_requests',
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    rejection_reason = models.CharField(
        max_length=30, choices=REJECTION_REASON_CHOICES, blank=True,
    )
    rejection_note = models.CharField(max_length=200, blank=True)
    request_code = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'property'],
                name='unique_interest_request_per_tenant_property',
            ),
        ]
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.request_code:
            self.request_code = f'REQ-{self.pk:05d}'
            super().save(update_fields=['request_code'])

            
    def __str__(self):
        return f"{self.tenant} -> {self.property} ({self.status})"