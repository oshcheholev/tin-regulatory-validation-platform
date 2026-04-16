from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Country, TinRule
from .serializers import CountrySerializer, TinRuleSerializer


@extend_schema(tags=['Rules'])
class CountryListView(generics.ListAPIView):
    """List all countries with extracted TIN rules."""
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']
    pagination_class = None  # Return all countries at once for dropdowns


@extend_schema(tags=['Rules'])
class CountryDetailView(generics.RetrieveAPIView):
    """Get a specific country details."""
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'code'


@extend_schema(tags=['Rules'])
class TinRuleListView(generics.ListAPIView):
    """List all TIN validation rules."""
    serializer_class = TinRuleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['country__code', 'rule_type', 'is_active']
    search_fields = ['description', 'country__name', 'country__code']
    ordering_fields = ['country__name', 'rule_type', 'confidence_score', 'created_at']

    def get_queryset(self):
        queryset = TinRule.objects.select_related('country', 'source_document').order_by('country__name', 'rule_type')
        country_code = self.request.query_params.get('country')
        if country_code:
            queryset = queryset.filter(country__code=country_code.upper())
        document_id = self.request.query_params.get('document_id')
        if document_id:
            queryset = queryset.filter(source_document_id=document_id)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        from django.db.models import Count
        counts = dict(queryset.values_list('is_active').annotate(count=Count('is_active')))
        status_counts = {
            'active': counts.get(True, 0),
            'inactive': counts.get(False, 0),
        }

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['status_counts'] = status_counts
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data, 'status_counts': status_counts})


@extend_schema(tags=['Rules'])
class TinRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific TIN rule."""
    queryset = TinRule.objects.select_related('country', 'source_document')
    serializer_class = TinRuleSerializer
    permission_classes = [IsAuthenticated]
