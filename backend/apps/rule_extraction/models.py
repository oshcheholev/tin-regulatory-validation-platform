from django.db import models
from apps.documents.models import RuleSourceDocument


class Country(models.Model):
    """Country with its TIN format rules."""
    code = models.CharField(max_length=2, unique=True)  # ISO 3166-1 alpha-2
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'countries'
        ordering = ['name']
        verbose_name_plural = 'countries'

    def __str__(self):
        return f'{self.name} ({self.code})'


class TinRule(models.Model):
    """Extracted TIN validation rule for a specific country."""

    RULE_TYPE_CHOICES = [
        ('format', 'Format'),
        ('length', 'Length'),
        ('checksum', 'Checksum'),
        ('character_set', 'Character Set'),
        ('structure', 'Structure'),
        ('other', 'Other'),
    ]

    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='tin_rules')
    source_document = models.ForeignKey(
        RuleSourceDocument, on_delete=models.SET_NULL, null=True, blank=True, related_name='tin_rules'
    )
    rule_type = models.CharField(max_length=50, choices=RULE_TYPE_CHOICES)
    description = models.TextField()
    regex_pattern = models.CharField(max_length=500, blank=True, null=True)
    min_length = models.PositiveIntegerField(null=True, blank=True)
    max_length = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    confidence_score = models.FloatField(default=1.0)
    raw_extraction = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tin_rules'
        ordering = ['country', 'rule_type']

    def __str__(self):
        return f'{self.country.code} - {self.rule_type}: {self.description[:60]}'
