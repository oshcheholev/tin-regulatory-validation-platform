from django.contrib import admin
from .models import Country, TinRule


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'created_at']
    search_fields = ['code', 'name']
    ordering = ['name']


@admin.register(TinRule)
class TinRuleAdmin(admin.ModelAdmin):
    list_display = ['country', 'rule_type', 'description', 'is_active', 'confidence_score']
    list_filter = ['rule_type', 'is_active', 'country']
    search_fields = ['description', 'country__name', 'country__code']
    ordering = ['country', 'rule_type']
