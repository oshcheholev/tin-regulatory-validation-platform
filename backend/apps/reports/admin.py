from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'format', 'status', 'total_records', 'created_by', 'created_at']
    list_filter = ['format', 'status']
    search_fields = ['name']
    ordering = ['-created_at']
