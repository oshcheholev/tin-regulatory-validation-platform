from django.urls import path
from .views import ReportListView, ReportCreateView, ReportDetailView, ReportDownloadView

urlpatterns = [
    path('', ReportListView.as_view(), name='report-list'),
    path('generate/', ReportCreateView.as_view(), name='report-generate'),
    path('<int:pk>/', ReportDetailView.as_view(), name='report-detail'),
    path('<int:pk>/download/', ReportDownloadView.as_view(), name='report-download'),
]
