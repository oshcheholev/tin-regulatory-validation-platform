from rest_framework import serializers
from .models import Country, TinRule


class CountrySerializer(serializers.ModelSerializer):
    rule_count = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ['id', 'code', 'name', 'rule_count', 'created_at']

    def get_rule_count(self, obj):
        return obj.tin_rules.filter(is_active=True).count()


class TinRuleSerializer(serializers.ModelSerializer):
    country_code = serializers.CharField(source='country.code', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    source_document_title = serializers.CharField(source='source_document.title', read_only=True, default=None)

    class Meta:
        model = TinRule
        fields = [
            'id', 'country_code', 'country_name', 'source_document_title',
            'rule_type', 'description', 'regex_pattern', 'min_length', 'max_length',
            'is_active', 'confidence_score', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
