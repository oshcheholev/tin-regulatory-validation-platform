from django.db import models
from apps.users.models import User


def document_upload_path(instance, filename):
    return f'documents/{instance.uploaded_by.id}/{filename}'


class RuleSourceDocument(models.Model):
    """OECD PDF document uploaded for TIN rule extraction."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=document_upload_path)
    file_size = models.PositiveIntegerField(default=0)
    file_hash = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    page_count = models.PositiveIntegerField(default=0)
    extracted_text = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='documents')
    task_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rule_source_documents'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class OECDSyncLog(models.Model):
    """Log for OECD PDF scraping/synchronization tasks."""
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_found = models.IntegerField(default=0)
    downloaded_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    error_details = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'oecd_sync_logs'
        ordering = ['-start_time']

    def __str__(self):
        return f"OECD Sync at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
