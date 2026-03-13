from django.db import models
from apps.users.models import User
from apps.validation.models import ValidationBatch


class Report(models.Model):
    """Generated validation report."""

    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    name = models.CharField(max_length=255)
    batch = models.ForeignKey(
        ValidationBatch, on_delete=models.CASCADE, null=True, blank=True, related_name='reports'
    )
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='csv')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    total_records = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.format.upper()})'
