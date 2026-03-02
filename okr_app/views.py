from .models import Objective, KeyResult, KeyResultHistory, RiskBlocker, Accomplishment, DecisionResource, Notification, AuditLog
from .serializers import (
    ObjectiveSerializer, KeyResultSerializer, KeyResultHistorySerializer,
    RiskBlockerSerializer, AccomplishmentSerializer, DecisionResourceSerializer,
    NotificationSerializer, AuditLogSerializer
)
from users_app.permissions import IsReadOnly, IsMember, AtLeastTeamLead, AtLeastCEO

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        org_id = self.request.auth.get('org_id')
        return Notification.objects.filter(organization_id=org_id, user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        org_id = self.request.auth.get('org_id')
        Notification.objects.filter(organization_id=org_id, user=self.request.user).update(is_read=True)
        return Response({'status': 'all marked as read'})

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, AtLeastTeamLead]

    def get_queryset(self):
        org_id = self.request.auth.get('org_id')
        return AuditLog.objects.filter(organization_id=org_id)

class BaseOrgScopedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsReadOnly]

    def get_queryset(self):
        # Use org_id from JWT token for isolation
        org_id = self.request.auth.get('org_id')
        if not org_id:
            # Fallback for internal calls or non-JWT auth if necessary
            membership = self.request.user.memberships.filter(is_active=True).first()
            org_id = membership.organization_id if membership else None
            
        return self.queryset.model.objects.for_org(org_id)

    def perform_create(self, serializer):
        org_id = self.request.auth.get('org_id')
        serializer.save(organization_id=org_id)

class ObjectiveViewSet(BaseOrgScopedViewSet):
    queryset = Objective.objects.all()
    serializer_class = ObjectiveSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsMember()]
        return super().get_permissions()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsMember])
    def submit_for_approval(self, request, pk=None):
        obj = self.get_object()
        if obj.status != 'draft':
            return Response({"error": "Only draft objectives can be submitted for approval"}, status=status.HTTP_400_BAD_REQUEST)
        
        obj.status = 'pending_approval'
        obj.save()
        return Response(ObjectiveSerializer(obj).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, AtLeastTeamLead])
    def approve(self, request, pk=None):
        obj = self.get_object()
        if obj.status != 'pending_approval':
            return Response({"error": "Only pending objectives can be approved"}, status=status.HTTP_400_BAD_REQUEST)
        
        obj.status = 'approved'
        obj.save()
        return Response(ObjectiveSerializer(obj).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, AtLeastTeamLead])
    def reject(self, request, pk=None):
        obj = self.get_object()
        reason = request.data.get('reason')
        if not reason:
            return Response({"error": "Rejection reason is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        if obj.status != 'pending_approval':
            return Response({"error": "Only pending objectives can be rejected"}, status=status.HTTP_400_BAD_REQUEST)
        
        obj.status = 'draft' # Or a dedicated 'rejected' status if model adds it
        obj.save()
        # In a real app, we'd log the reason in a comment or audit log
        return Response(ObjectiveSerializer(obj).data)

class KeyResultViewSet(BaseOrgScopedViewSet):
    queryset = KeyResult.objects.all()
    serializer_class = KeyResultSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'log_update']:
            return [permissions.IsAuthenticated(), IsMember()]
        return super().get_permissions()

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

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsMember()]
        return super().get_permissions()

class AccomplishmentViewSet(BaseOrgScopedViewSet):
    queryset = Accomplishment.objects.all()
    serializer_class = AccomplishmentSerializer
    filterset_fields = ['key_result']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsMember()]
        return super().get_permissions()

class DecisionResourceViewSet(BaseOrgScopedViewSet):
    queryset = DecisionResource.objects.all()
    serializer_class = DecisionResourceSerializer
    filterset_fields = ['key_result', 'status']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsMember()]
        return super().get_permissions()
