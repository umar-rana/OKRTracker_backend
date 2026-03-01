from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Objective, KeyResult, KeyResultHistory, RiskBlocker, Accomplishment, DecisionResource
from .serializers import (
    ObjectiveSerializer, KeyResultSerializer, KeyResultHistorySerializer,
    RiskBlockerSerializer, AccomplishmentSerializer, DecisionResourceSerializer
)

class BaseOrgScopedViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        # Enforce organization isolation using the custom manager
        org_id = self.request.user.memberships.filter(is_active=True).first().organization_id
        return self.queryset.model.objects.for_org(org_id)

    def perform_create(self, serializer):
        org_id = self.request.user.memberships.filter(is_active=True).first().organization_id
        serializer.save(organization_id=org_id)

class ObjectiveViewSet(BaseOrgScopedViewSet):
    queryset = Objective.objects.all()
    serializer_class = ObjectiveSerializer

class KeyResultViewSet(BaseOrgScopedViewSet):
    queryset = KeyResult.objects.all()
    serializer_class = KeyResultSerializer

    @action(detail=True, methods=['post'])
    def log_update(self, request, pk=None):
        kr = self.get_object()
        new_value = request.data.get('current_value')
        new_rag_status = request.data.get('rag_status')
        note = request.data.get('note', '')

        if new_value is None or new_rag_status is None:
            return Response({"error": "current_value and rag_status are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Record history
        KeyResultHistory.objects.create(
            key_result=kr,
            previous_value=kr.current_value,
            new_value=new_value,
            previous_rag_status=kr.rag_status,
            new_rag_status=new_rag_status,
            updated_by=request.user,
            note=note
        )

        # Update KR
        kr.current_value = new_value
        kr.rag_status = new_rag_status
        kr.save()

        return Response(KeyResultSerializer(kr).data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        kr = self.get_object()
        history = kr.history.all()
        serializer = KeyResultHistorySerializer(history, many=True)
        return Response(serializer.data)

class RiskBlockerViewSet(BaseOrgScopedViewSet):
    queryset = RiskBlocker.objects.all()
    serializer_class = RiskBlockerSerializer
    filterset_fields = ['key_result', 'status', 'impact']

class AccomplishmentViewSet(BaseOrgScopedViewSet):
    queryset = Accomplishment.objects.all()
    serializer_class = AccomplishmentSerializer
    filterset_fields = ['key_result']

class DecisionResourceViewSet(BaseOrgScopedViewSet):
    queryset = DecisionResource.objects.all()
    serializer_class = DecisionResourceSerializer
    filterset_fields = ['key_result', 'status']

class RiskBlockerViewSet(BaseOrgScopedViewSet):
    queryset = RiskBlocker.objects.all()
    serializer_class = RiskBlockerSerializer
    filterset_fields = ['key_result', 'status', 'impact']

class AccomplishmentViewSet(BaseOrgScopedViewSet):
    queryset = Accomplishment.objects.all()
    serializer_class = AccomplishmentSerializer
    filterset_fields = ['key_result']

class DecisionResourceViewSet(BaseOrgScopedViewSet):
    queryset = DecisionResource.objects.all()
    serializer_class = DecisionResourceSerializer
    filterset_fields = ['key_result', 'status']
