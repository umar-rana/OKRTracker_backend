from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
import json
from .models import Objective, KeyResult, RiskBlocker, Accomplishment, DecisionResource, AuditLog, Notification

def get_serialized_model(instance):
    data = model_to_dict(instance)
    # Convert UUIDs and Dates to strings for JSON
    for key, value in data.items():
        if hasattr(value, 'hex'): # UUID
            data[key] = str(value)
        elif hasattr(value, 'isoformat'): # Date/DateTime
            data[key] = value.isoformat()
    return data

@receiver(post_save, sender=Objective)
@receiver(post_save, sender=KeyResult)
@receiver(post_save, sender=RiskBlocker)
@receiver(post_save, sender=Accomplishment)
@receiver(post_save, sender=DecisionResource)
def log_save(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    AuditLog.objects.create(
        organization=instance.organization,
        performed_by=getattr(instance, 'updated_by', getattr(instance, 'owner', getattr(instance, 'logged_by', getattr(instance, 'requested_by', None)))),
        action=action,
        entity_type=sender.__name__,
        entity_id=instance.id,
        new_state=get_serialized_model(instance)
    )

@receiver(post_delete, sender=Objective)
@receiver(post_delete, sender=KeyResult)
@receiver(post_delete, sender=RiskBlocker)
@receiver(post_delete, sender=Accomplishment)
@receiver(post_delete, sender=DecisionResource)
def log_delete(sender, instance, **kwargs):
    AuditLog.objects.create(
        organization=instance.organization,
        performed_by=getattr(instance, 'owner', getattr(instance, 'logged_by', None)),
        action='delete',
        entity_type=sender.__name__,
        entity_id=instance.id,
        previous_state=get_serialized_model(instance)
    )

# Notification triggers
@receiver(post_save, sender=Objective)
def trigger_objective_notifications(sender, instance, created, **kwargs):
    if instance.status == 'pending_approval':
        # Notify CEO/Platform Admin (simplified: notify all admins in org)
        admins = instance.organization.memberships.filter(role__in=['ceo', 'platform_admin'])
        for admin in admins:
            Notification.objects.create(
                user=admin.user,
                organization=instance.organization,
                type='objective_submitted',
                title='Objective Pending Approval',
                body=f"Objective '{instance.title}' has been submitted for approval.",
                entity_type='Objective',
                entity_id=instance.id
            )
    elif instance.status == 'approved':
        Notification.objects.create(
            user=instance.owner,
            organization=instance.organization,
            type='objective_approved',
            title='Objective Approved',
            body=f"Your objective '{instance.title}' has been approved.",
            entity_type='Objective',
            entity_id=instance.id
        )

@receiver(post_save, sender=RiskBlocker)
def trigger_risk_notifications(sender, instance, created, **kwargs):
    if created and instance.impact == 'high':
        # Notify owners and leads
        Notification.objects.create(
            user=instance.key_result.owner,
            organization=instance.organization,
            type='high_risk_identified',
            title='High Impact Risk Identified',
            body=f"A high impact risk '{instance.title}' was logged for KR '{instance.key_result.title}'.",
            entity_type='RiskBlocker',
            entity_id=instance.id
        )
