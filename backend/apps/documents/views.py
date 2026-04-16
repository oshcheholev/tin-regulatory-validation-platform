from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import RuleSourceDocument, OECDSyncLog
from .serializers import RuleSourceDocumentSerializer, DocumentUploadSerializer
from apps.rule_extraction.tasks import process_document_task
import threading

@extend_schema(tags=['Documents'])
class DocumentListView(generics.ListAPIView):
    """List all uploaded OECD documents."""
    serializer_class = RuleSourceDocumentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title', 'status']

    def get_queryset(self):
        return RuleSourceDocument.objects.all().order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        from django.db.models import Count
        counts = dict(queryset.values_list('status').annotate(count=Count('status')))
        status_counts = {
            'completed': counts.get('completed', 0),
            'failed': counts.get('failed', 0),
            'processing': counts.get('processing', 0),
            'pending': counts.get('pending', 0),
        }

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['status_counts'] = status_counts
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'status_counts': status_counts
        })


@extend_schema(tags=['Documents'])
class DocumentUploadView(generics.CreateAPIView):
    """Upload a new OECD PDF document for TIN rule extraction."""
    serializer_class = DocumentUploadSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()

        # Trigger async processing
        task = process_document_task.delay(document.id)
        document.task_id = task.id
        document.status = 'processing'
        document.save(update_fields=['task_id', 'status'])

        response_serializer = RuleSourceDocumentSerializer(document, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Documents'])
class DocumentDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete an OECD document."""
    queryset = RuleSourceDocument.objects.all()
    serializer_class = RuleSourceDocumentSerializer
    permission_classes = [IsAuthenticated]

@extend_schema(tags=['Documents'], responses={200: dict})
class OECDSyncView(views.APIView):
    """Trigger an OECD website sync and return status."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Check if already running
        running = OECDSyncLog.objects.filter(status='running').first()
        if running:
            return Response({"status": "already_running", "log_id": running.id}, status=status.HTTP_400_BAD_REQUEST)
        
        log = OECDSyncLog.objects.create()
        from .scraper import run_oecd_sync
        # Start in background thread so API responds quickly
        thread = threading.Thread(target=run_oecd_sync, args=(log.id, request.user.id))
        thread.start()
        
        return Response({"status": "started", "log_id": log.id}, status=status.HTTP_202_ACCEPTED)

    def get(self, request, *args, **kwargs):
        # Return latest sync log
        log = OECDSyncLog.objects.order_by('-start_time').first()
        total_docs = RuleSourceDocument.objects.count()
        if not log:
            return Response({
                "status": "not_started", 
                "total_docs": total_docs, 
                "total_found": 0, 
                "downloaded_count": 0, 
                "error_count": 0, 
                "error_details": {}
            })
        
        return Response({
            "status": log.status,
            "total_docs": total_docs,
            "total_found": log.total_found,
            "downloaded_count": log.downloaded_count,
            "error_count": log.error_count,
            "error_details": log.error_details,
            "start_time": log.start_time,
            "end_time": log.end_time,
        })
