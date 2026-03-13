from django.db import models
from apps.users.models import User
from apps.rule_extraction.models import Country, TinRule


class ValidationResult(models.Model):
    """Result of a TIN validation check."""

    STATUS_CHOICES = [
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
        ('unknown', 'Unknown'),
    ]

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='validation_results')
    tin = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    is_valid = models.BooleanField()
    matched_rules = models.ManyToManyField(TinRule, blank=True, related_name='validation_results')
    failed_rules = models.ManyToManyField(TinRule, blank=True, related_name='failed_validation_results')
    explanation = models.TextField(blank=True)
    validated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='validation_results'
    )
    # For batch validation jobs
    batch_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'validation_results'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.country_id}/{self.tin} → {self.status}'


class ValidationBatch(models.Model):
    """Batch TIN validation job."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_count = models.PositiveIntegerField(default=0)
    valid_count = models.PositiveIntegerField(default=0)
    invalid_count = models.PositiveIntegerField(default=0)
    unknown_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    csv_file = models.FileField(upload_to='validation_batches/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='validation_batches')
    task_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'validation_batches'
        ordering = ['-created_at']

    def __str__(self):
        return f'Batch {self.name} ({self.status})'
