from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import ValidationResult, ValidationBatch
from .serializers import (
    TinValidationRequestSerializer,
    TinValidationResponseSerializer,
    ValidationResultSerializer,
    ValidationBatchSerializer,
    BatchUploadSerializer,
)
from .engine import validate_tin
from .tasks import process_batch_validation_task
from apps.rule_extraction.models import Country, TinRule


@extend_schema(tags=['Validation'])
class ValidateTinView(APIView):
    """
    Validate a single TIN against extracted OECD rules.

    POST /api/v1/validation/validate/
    Input: { country: "US", tin: "123-45-6789" }
    Output: validation result with rule explanation
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=TinValidationRequestSerializer,
        responses={200: TinValidationResponseSerializer},
    )
    def post(self, request):
        serializer = TinValidationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        country_code = serializer.validated_data['country'].upper()
        tin = serializer.validated_data['tin']

        validation = validate_tin(country_code, tin)

        # Persist result
        result = ValidationResult(
            tin=tin,
            is_valid=validation['is_valid'],
            status=validation['status'],
            explanation=validation['explanation'],
            validated_by=request.user,
        )
        try:
            country = Country.objects.get(code=country_code)
            result.country = country
        except Country.DoesNotExist:
            pass
        result.save()

        if validation['matched_rule_ids']:
            result.matched_rules.set(validation['matched_rule_ids'])
        if validation['failed_rule_ids']:
            result.failed_rules.set(validation['failed_rule_ids'])

        response_serializer = TinValidationResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['Validation'])
class ValidationResultListView(generics.ListAPIView):
    """List validation history."""
    serializer_class = ValidationResultSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'is_valid', 'country__code']
    search_fields = ['tin', 'country__name']
    ordering_fields = ['created_at', 'status']

    def get_queryset(self):
        return ValidationResult.objects.select_related('country').filter(batch_id='')


@extend_schema(tags=['Validation'])
class ValidationResultDetailView(generics.RetrieveAPIView):
    """Get details of a specific validation result."""
    queryset = ValidationResult.objects.select_related('country').prefetch_related('matched_rules')
    serializer_class = TinValidationResponseSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(tags=['Validation'])
class BatchValidationView(generics.CreateAPIView):
    """Upload a CSV file with multiple TINs for batch validation."""
    serializer_class = BatchUploadSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        batch = ValidationBatch(
            name=serializer.validated_data['name'],
            csv_file=serializer.validated_data['csv_file'],
            created_by=request.user,
        )
        batch.save()

        task = process_batch_validation_task.delay(batch.id)
        batch.task_id = task.id
        batch.status = 'processing'
        batch.save(update_fields=['task_id', 'status'])

        return Response(ValidationBatchSerializer(batch).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Validation'])
class BatchListView(generics.ListAPIView):
    """List all batch validation jobs."""
    serializer_class = ValidationBatchSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status']
    ordering_fields = ['created_at', 'status']

    def get_queryset(self):
        return ValidationBatch.objects.filter(created_by=self.request.user)


@extend_schema(tags=['Validation'])
class BatchDetailView(generics.RetrieveAPIView):
    """Get details of a specific batch validation job."""
    queryset = ValidationBatch.objects.all()
    serializer_class = ValidationBatchSerializer
    permission_classes = [IsAuthenticated]


@extend_schema(tags=['Validation'])
class BatchResultsView(generics.ListAPIView):
    """List all validation results for a specific batch."""
    serializer_class = ValidationResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        batch_id = self.kwargs['batch_id']
        return ValidationResult.objects.filter(batch_id=str(batch_id)).select_related('country')
