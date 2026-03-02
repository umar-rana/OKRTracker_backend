from rest_framework import permissions
from rest_framework.views import APIView
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
import weasyprint
from .models import Objective

class ExportOKRReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, orgId):
        # 1. Verify user belongs to this organization
        if not request.user.memberships.filter(organization_id=orgId, is_active=True).exists():
            raise PermissionDenied("You do not have access to this organization's reports.")

        # 2. Fetch data
        objectives = Objective.objects.filter(organization_id=orgId).prefetch_related('key_results')
        
        if not objectives.exists():
            return HttpResponse("No objectives found for this organization.", status=404)

        html_content = render_to_string('reports/okr_report.html', {
            'objectives': objectives,
            'organization': objectives.first().organization
        })
        
        pdf = weasyprint.HTML(string=html_content).write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="OKR_Report_{orgId}.pdf"'
        return response
