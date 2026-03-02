from django.db import models

class OrganizationManager(models.Manager):
    def for_org(self, organization_id):
        """
        Filters the queryset by organization_id.
        Expected to be used in ViewSets to enforce data isolation.
        """
        return self.get_queryset().filter(organization_id=organization_id)
