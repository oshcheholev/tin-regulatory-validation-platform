import hashlib
from rest_framework import serializers
from .models import RuleSourceDocument


class RuleSourceDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = RuleSourceDocument
        fields = [
            'id', 'title', 'description', 'file_url', 'file_size',
            'file_hash', 'status', 'error_message', 'page_count',
            'uploaded_by_email', 'task_id', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'file_size', 'file_hash', 'status', 'error_message',
                            'page_count', 'task_id', 'created_at', 'updated_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class DocumentUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = RuleSourceDocument
        fields = ['title', 'description', 'file']

    def validate_file(self, value):
        if value.content_type not in ['application/pdf']:
            raise serializers.ValidationError('Only PDF files are allowed.')
        max_size = 20 * 1024 * 1024  # 20 MB
        if value.size > max_size:
            raise serializers.ValidationError('File size cannot exceed 20MB.')
        return value

    def create(self, validated_data):
        file = validated_data['file']
        # Compute hash for deduplication
        md5 = hashlib.md5()
        for chunk in file.chunks():
            md5.update(chunk)
        file_hash = md5.hexdigest()

        doc = RuleSourceDocument(
            title=validated_data['title'],
            description=validated_data.get('description', ''),
            file=file,
            file_size=file.size,
            file_hash=file_hash,
            uploaded_by=self.context['request'].user,
        )
        doc.save()
        return doc
