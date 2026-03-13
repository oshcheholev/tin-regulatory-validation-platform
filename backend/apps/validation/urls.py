from django.urls import path
from .views import (
    ValidateTinView,
    ValidationResultListView,
    ValidationResultDetailView,
    BatchValidationView,
    BatchListView,
    BatchDetailView,
    BatchResultsView,
)

urlpatterns = [
    path('validate/', ValidateTinView.as_view(), name='tin-validate'),
    path('results/', ValidationResultListView.as_view(), name='validation-result-list'),
    path('results/<int:pk>/', ValidationResultDetailView.as_view(), name='validation-result-detail'),
    path('batch/', BatchListView.as_view(), name='batch-list'),
    path('batch/upload/', BatchValidationView.as_view(), name='batch-upload'),
    path('batch/<int:pk>/', BatchDetailView.as_view(), name='batch-detail'),
    path('batch/<int:batch_id>/results/', BatchResultsView.as_view(), name='batch-results'),
]
