from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    file_url = serializers.SerializerMethodField()
    batch_name = serializers.CharField(source='batch.name', read_only=True, default=None)

    class Meta:
        model = Report
        fields = [
            'id', 'name', 'batch_name', 'format', 'status', 'file_url',
            'total_records', 'error_message', 'created_by_email', 'created_at', 'completed_at',
        ]

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class ReportCreateSerializer(serializers.Serializer):
    batch_id = serializers.IntegerField(required=False, allow_null=True)
    format = serializers.ChoiceField(choices=['csv', 'json'], default='csv')
    name = serializers.CharField(max_length=255, required=False)
