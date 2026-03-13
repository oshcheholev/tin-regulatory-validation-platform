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
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='documents')
    task_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rule_source_documents'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
