from django.db import models

class OrganizationManager(models.Manager):
    def for_org(self, organization_id):
        return self.get_queryset().filter(organization_id=organization_id)
