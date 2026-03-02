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
        # 1. Verify user's JWT org_id matches the requested orgId
        jwt_org_id = request.auth.get('org_id')
        if not jwt_org_id or str(jwt_org_id) != str(orgId):
            raise PermissionDenied("You do not have access to this organization's reports.")

        # 2. Fetch data using OrganizationManager
        objectives = Objective.objects.for_org(orgId).prefetch_related('key_results', 'owner')
        
        # Get organization name for filename
        from users_app.models import Organization
        try:
            org = Organization.objects.get(id=orgId)
        except Organization.DoesNotExist:
            return HttpResponse("Organization not found.", status=404)

        if not objectives.exists():
            # Still show the template if organization exists but has no OKRs
            pass

        from django.utils import timezone
        html_content = render_to_string('reports/okr_report.html', {
            'objectives': objectives,
            'organization': org,
            'now': timezone.now()
        })
        
        pdf = weasyprint.HTML(string=html_content).write_pdf()
        
        filename = f"{org.name.replace(' ', '_')}_OKR_Report_{timezone.now().strftime('%Y%m%d')}.pdf"
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
