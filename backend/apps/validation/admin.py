from django.contrib import admin
from .models import ValidationResult, ValidationBatch


@admin.register(ValidationResult)
class ValidationResultAdmin(admin.ModelAdmin):
    list_display = ['country', 'tin', 'status', 'is_valid', 'validated_by', 'created_at']
    list_filter = ['status', 'is_valid', 'country']
    search_fields = ['tin', 'country__name']
    ordering = ['-created_at']


@admin.register(ValidationBatch)
class ValidationBatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'total_count', 'valid_count', 'invalid_count', 'created_by', 'created_at']
    list_filter = ['status']
    ordering = ['-created_at']
