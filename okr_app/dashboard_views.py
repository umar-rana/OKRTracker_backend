from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count, Avg
from .models import Objective, KeyResult, AuditLog
from users_app.permissions import IsMember

class DashboardAggregatorView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsMember]

    def get(self, request, orgId):
        # Verify JWT org_id
        jwt_org_id = request.auth.get('org_id')
        if str(jwt_org_id) != str(orgId):
            return Response({"error": "Unauthorized access to this organization"}, status=403)

        # 1. Overall Stats
        objectives = Objective.objects.filter(organization_id=orgId)
        total_objectives = objectives.count()
        
        krs = KeyResult.objects.filter(objective__organization_id=orgId)
        total_krs = krs.count()
        
        # 2. Health Distribution (Pie Chart Data)
        health_dist = krs.values('rag_status').annotate(count=Count('id'))
        # Convert to format: [{ name: 'On Track', value: 12, color: '#10B981' }, ...]
        color_map = {
            'green': '#10B981',
            'amber': '#F59E0B',
            'red': '#EF4444'
        }
        label_map = {
            'green': 'On Track',
            'amber': 'At Risk',
            'red': 'Critical'
        }
        pie_data = [
            {
                'name': label_map.get(item['rag_status'], item['rag_status']),
                'value': item['count'],
                'color': color_map.get(item['rag_status'], '#9CA3AF')
            }
            for item in health_dist
        ]

        # 3. Top Objectives Progress (Bar Chart Data)
        # For simplicity, average progress of KRs per objective
        top_objectives = objectives.annotate(
            avg_progress=Avg('key_results__current_value') # This is a simplification; real logic would normalize values
        ).order_by('-created_at')[:5]

        bar_data = [
            {
                'name': obj.title[:20] + ('...' if len(obj.title) > 20 else ''),
                'progress': 45, # Placeholder for real normalized progress logic
                'status': obj.status
            }
            for obj in top_objectives
        ]

        # 4. Recent Activity (Already exists in AuditLogViewSet, but can include summary here)
        recent_activity = AuditLog.objects.filter(organization_id=orgId).order_by('-performed_at')[:5]
        activity_data = [
            {
                'id': log.id,
                'action': log.action,
                'user': log.performed_by.get_full_name() or log.performed_by.username,
                'timestamp': log.performed_at
            }
            for log in recent_activity
        ]

        return Response({
            'stats': {
                'total_objectives': total_objectives,
                'total_krs': total_krs,
                'active_teams': 4, # Placeholder
                'completion_rate': 68 # Placeholder
            },
            'health_distribution': pie_data,
            'top_objectives': bar_data,
            'recent_activity': activity_data
        })
