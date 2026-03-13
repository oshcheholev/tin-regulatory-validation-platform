from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
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
        queryset = TinRule.objects.select_related('country', 'source_document')
        country_code = self.request.query_params.get('country')
        if country_code:
            queryset = queryset.filter(country__code=country_code.upper())
        return queryset


@extend_schema(tags=['Rules'])
class TinRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific TIN rule."""
    queryset = TinRule.objects.select_related('country', 'source_document')
    serializer_class = TinRuleSerializer
    permission_classes = [IsAuthenticated]
