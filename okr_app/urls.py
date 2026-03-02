from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ObjectiveViewSet, KeyResultViewSet, 
    RiskBlockerViewSet, AccomplishmentViewSet, DecisionResourceViewSet,
    NotificationViewSet, AuditLogViewSet
)
from .export_views import ExportOKRReportView
from .dashboard_views import DashboardAggregatorView

router = DefaultRouter()
# ... (router registrations)

urlpatterns = [
    path('orgs/<uuid:orgId>/export/', ExportOKRReportView.as_view(), name='export_okrs'),
    path('orgs/<uuid:orgId>/dashboard/', DashboardAggregatorView.as_view(), name='dashboard_aggregator'),
    path('orgs/<uuid:orgId>/', include(router.urls)),
]
