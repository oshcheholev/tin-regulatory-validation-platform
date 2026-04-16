from django.urls import path
from .views import DocumentListView, DocumentUploadView, DocumentDetailView, OECDSyncView

urlpatterns = [
    path('', DocumentListView.as_view(), name='document-list'),
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('oecd-sync/', OECDSyncView.as_view(), name='oecd-sync'),
    path('<int:pk>/', DocumentDetailView.as_view(), name='document-detail'),
]
