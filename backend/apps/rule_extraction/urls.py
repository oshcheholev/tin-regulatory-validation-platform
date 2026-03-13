from django.urls import path
from .views import CountryListView, CountryDetailView, TinRuleListView, TinRuleDetailView

urlpatterns = [
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('countries/<str:code>/', CountryDetailView.as_view(), name='country-detail'),
    path('', TinRuleListView.as_view(), name='tinrule-list'),
    path('<int:pk>/', TinRuleDetailView.as_view(), name='tinrule-detail'),
]
