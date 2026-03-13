import os
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import Report
from .serializers import ReportSerializer, ReportCreateSerializer
from .generators import generate_csv_report, generate_json_report
from apps.validation.models import ValidationResult, ValidationBatch


@extend_schema(tags=['Reports'])
class ReportListView(generics.ListAPIView):
    """List all generated reports."""
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(created_by=self.request.user)


@extend_schema(tags=['Reports'])
class ReportCreateView(APIView):
    """Generate a new validation report."""
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ReportCreateSerializer, responses={201: ReportSerializer})
    def post(self, request):
        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        batch_id = serializer.validated_data.get('batch_id')
        fmt = serializer.validated_data.get('format', 'csv')
        name = serializer.validated_data.get('name', f'Report-{timezone.now().strftime("%Y%m%d%H%M%S")}')

        # Get results
        if batch_id:
            try:
                batch = ValidationBatch.objects.get(id=batch_id)
            except ValidationBatch.DoesNotExist:
                return Response({'error': 'Batch not found'}, status=status.HTTP_404_NOT_FOUND)
            results = ValidationResult.objects.filter(batch_id=str(batch_id)).select_related('country')
        else:
            results = ValidationResult.objects.all().select_related('country')
            batch = None

        # Generate file
        if fmt == 'csv':
            content = generate_csv_report(results)
            filename = f'{name}.csv'
        else:
            content = generate_json_report(results)
            filename = f'{name}.json'

        report = Report(
            name=name,
            batch=batch,
            format=fmt,
            status='completed',
            total_records=results.count(),
            created_by=request.user,
            completed_at=timezone.now(),
        )
        report.save()
        report.file.save(filename, ContentFile(content), save=True)

        return Response(ReportSerializer(report, context={'request': request}).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Reports'])
class ReportDetailView(generics.RetrieveAPIView):
    """Get details of a specific report."""
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(created_by=self.request.user)


@extend_schema(tags=['Reports'])
class ReportDownloadView(APIView):
    """Download a report file."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            report = Report.objects.get(id=pk, created_by=request.user)
        except Report.DoesNotExist:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)

        if not report.file:
            return Response({'error': 'Report file not available'}, status=status.HTTP_404_NOT_FOUND)

        content_types = {
            'csv': 'text/csv',
            'json': 'application/json',
        }
        content_type = content_types.get(report.format, 'application/octet-stream')
        filename = os.path.basename(report.file.name)

        response = HttpResponse(report.file.read(), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
