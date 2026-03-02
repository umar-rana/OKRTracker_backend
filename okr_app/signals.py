from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Objective, KeyResult, KeyResultHistory, RiskBlocker, DecisionResource, Notification, AuditLog
import json
from django.core.serializers.json import DjangoJSONEncoder

def serialize_model(instance):
    data = {}
    for field in instance._meta.fields:
        data[field.name] = str(getattr(instance, field.name))
    return data

@receiver(post_save, sender=Objective)
@receiver(post_save, sender=KeyResult)
@receiver(post_save, sender=RiskBlocker)
@receiver(post_save, sender=DecisionResource)
def create_audit_log(sender, instance, created, **kwargs):
    action = f"{sender.__name__.lower()}.{'created' if created else 'updated'}"
    
    # In a real scenario, we'd get the current user from middleware
    # For now, we use a placeholder or the instance owner if available
    user = getattr(instance, 'owner', None) or getattr(instance, 'logged_by', None) or getattr(instance, 'user', None)
    
    if user:
        AuditLog.objects.create(
            organization=instance.organization,
            performed_by=user,
            action=action,
            entity_type=sender.__name__,
            entity_id=instance.id,
            new_state=serialize_model(instance)
        )

@receiver(post_save, sender=Objective)
def notify_objective_status_change(sender, instance, created, **kwargs):
    if created:
        return # Handled by audit log or specific 'submit' logic if needed
        
    # Check if status changed
    # In a real app we'd use a tracker like django-model-utils
    # For now, we'll assume the view calls update and we check instance state
    
    from .models import Notification
    from users_app.models import Membership
    
    if instance.status == 'pending_approval':
        # Notify Team Lead and CEO
        stakeholders = Membership.objects.filter(
            organization=instance.organization,
            role__in=['ceo', 'team_lead']
        ).select_related('user')
        
        for m in stakeholders:
            Notification.objects.create(
                user=m.user,
                organization=instance.organization,
                type='objective_pending',
                title="Objective Pending Approval",
                body=f"'{instance.title}' has been submitted for approval by {instance.owner.get_full_name()}.",
                entity_type='Objective',
                entity_id=instance.id
            )
            
    elif instance.status == 'approved':
        # Notify creator
        Notification.objects.create(
            user=instance.owner,
            organization=instance.organization,
            type='objective_approved',
            title="Objective Approved",
            body=f"Your objective '{instance.title}' has been approved.",
            entity_type='Objective',
            entity_id=instance.id
        )
        
    elif instance.status == 'rejected':
        # Notify creator with reason
        Notification.objects.create(
            user=instance.owner,
            organization=instance.organization,
            type='objective_rejected',
            title="Objective Rejected",
            body=f"Your objective '{instance.title}' was rejected. Reason: {instance.rejection_reason}",
            entity_type='Objective',
            entity_id=instance.id
        )

@receiver(post_save, sender=KeyResult)
def notify_rag_change(sender, instance, **kwargs):
    if instance.rag_status == 'red':
        from .models import Notification
        from users_app.models import Membership
        stakeholders = Membership.objects.filter(
            organization=instance.organization,
            role__in=['ceo', 'team_lead']
        ).select_related('user')
        
        for m in stakeholders:
            Notification.objects.create(
                user=m.user,
                organization=instance.organization,
                type='kr_red_alert',
                title=f"Red Alert: {instance.title}",
                body=f"Key Result '{instance.title}' has been marked as Red.",
                entity_type='KeyResult',
                entity_id=instance.id
            )

@receiver(post_save, sender=RiskBlocker)
def notify_red_risk(sender, instance, created, **kwargs):
    if instance.rag_status == 'red':
        from .models import Notification
        from users_app.models import Membership
        stakeholders = Membership.objects.filter(
            organization=instance.organization,
            role__in=['ceo', 'team_lead']
        ).select_related('user')
        
        for m in stakeholders:
            Notification.objects.create(
                user=m.user,
                organization=instance.organization,
                type='risk_red_alert',
                title=f"High Risk Alert: {instance.title}",
                body=f"A new Red Risk has been logged for KR '{instance.key_result.title}'.",
                entity_type='RiskBlocker',
                entity_id=instance.id
            )

@receiver(post_save, sender=DecisionResource)
def notify_decision_request(sender, instance, created, **kwargs):
    from .models import Notification
    if created:
        Notification.objects.create(
            user=instance.decision_owner,
            organization=instance.organization,
            type='decision_requested',
            title="Decision Required",
            body=f"{instance.requested_by.get_full_name()} requested a decision: {instance.title}",
            entity_type='DecisionResource',
            entity_id=instance.id
        )
    elif instance.status in ['approved', 'rejected']:
        Notification.objects.create(
            user=instance.requested_by,
            organization=instance.organization,
            type=f'decision_{instance.status}',
            title=f"Decision {instance.status.capitalize()}",
            body=f"Your decision request '{instance.title}' has been {instance.status}.",
            entity_type='DecisionResource',
            entity_id=instance.id
        )
