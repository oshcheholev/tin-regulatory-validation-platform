from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import RuleSourceDocument
from .serializers import RuleSourceDocumentSerializer, DocumentUploadSerializer
from apps.rule_extraction.tasks import process_document_task


@extend_schema(tags=['Documents'])
class DocumentListView(generics.ListAPIView):
    """List all uploaded OECD documents."""
    serializer_class = RuleSourceDocumentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title', 'status']

    def get_queryset(self):
        return RuleSourceDocument.objects.all()


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
