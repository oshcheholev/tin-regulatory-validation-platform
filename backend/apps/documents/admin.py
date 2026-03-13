from django.contrib import admin
from .models import RuleSourceDocument


@admin.register(RuleSourceDocument)
class RuleSourceDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'page_count', 'file_size', 'uploaded_by', 'created_at']
    list_filter = ['status']
    search_fields = ['title', 'description']
    readonly_fields = ['file_hash', 'file_size', 'page_count', 'task_id', 'created_at', 'updated_at']
