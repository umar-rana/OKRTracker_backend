from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ObjectiveViewSet, KeyResultViewSet, 
    RiskBlockerViewSet, AccomplishmentViewSet, DecisionResourceViewSet
)
from .export_views import ExportOKRReportView

router = DefaultRouter()
router.register(r'objectives', ObjectiveViewSet)
router.register(r'key-results', KeyResultViewSet)
router.register(r'risks', RiskBlockerViewSet)
router.register(r'accomplishments', AccomplishmentViewSet)
router.register(r'decisions', DecisionResourceViewSet)

urlpatterns = [
    path('orgs/<uuid:orgId>/export/', ExportOKRReportView.as_view(), name='export_okrs'),
    path('orgs/<uuid:orgId>/', include(router.urls)),
]
