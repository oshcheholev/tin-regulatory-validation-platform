from rest_framework import serializers
from .models import ValidationResult, ValidationBatch
from apps.rule_extraction.serializers import CountrySerializer, TinRuleSerializer


class TinValidationRequestSerializer(serializers.Serializer):
    country = serializers.CharField(max_length=2, help_text='ISO 3166-1 alpha-2 country code (e.g. US, GB, DE)')
    tin = serializers.CharField(max_length=100, help_text='Tax Identification Number to validate')


class TinValidationResponseSerializer(serializers.ModelSerializer):
    country_code = serializers.CharField(source='country.code', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    matched_rules = TinRuleSerializer(many=True, read_only=True)

    class Meta:
        model = ValidationResult
        fields = [
            'id', 'country_code', 'country_name', 'tin', 'is_valid',
            'status', 'explanation', 'matched_rules', 'created_at',
        ]


class ValidationResultSerializer(serializers.ModelSerializer):
    country_code = serializers.CharField(source='country.code', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = ValidationResult
        fields = [
            'id', 'country_code', 'country_name', 'tin', 'is_valid',
            'status', 'explanation', 'batch_id', 'created_at',
        ]


class ValidationBatchSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)

    class Meta:
        model = ValidationBatch
        fields = [
            'id', 'name', 'status', 'total_count', 'valid_count', 'invalid_count', 'unknown_count',
            'error_message', 'created_by_email', 'task_id', 'created_at', 'completed_at',
        ]
        read_only_fields = ['id', 'status', 'total_count', 'valid_count', 'invalid_count',
                            'unknown_count', 'error_message', 'task_id', 'created_at', 'completed_at']


class BatchUploadSerializer(serializers.ModelSerializer):
    csv_file = serializers.FileField()

    class Meta:
        model = ValidationBatch
        fields = ['name', 'csv_file']

    def validate_csv_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError('Only CSV files are allowed.')
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError('CSV file cannot exceed 10MB.')
        return value
