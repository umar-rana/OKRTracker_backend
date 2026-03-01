import weasyprint
from django.template.loader import render_to_string
from django.http import HttpResponse
from rest_framework.views import APIView
from .models import Objective

class ExportOKRReportView(APIView):
    def get(self, request, orgId):
        # We need to ensure we only export what the user has access to
        # But for this view, we'll use the provided orgId
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
