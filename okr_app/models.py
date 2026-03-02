import uuid
from django.db import models
from users_app.models import User, Organization, Team
from .managers import OrganizationManager

class Objective(models.Model):
    objects = OrganizationManager()
    PRIORITIES = [('p0', 'P0'), ('p1', 'P1'), ('p2', 'P2'), ('p3', 'P3')]
    STATUSES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='objectives')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='objectives')
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=5, choices=PRIORITIES, default='p2')
    status = models.CharField(max_length=20, choices=STATUSES, default='draft')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owned_objectives')
    co_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='co_owned_objectives')
    due_date = models.DateField()
    rejection_reason = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_objectives')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['organization', 'status'], name='obj_org_status_idx'),
        ]

    def __str__(self):
        return self.title

class KeyResult(models.Model):
    objects = OrganizationManager()
    KR_TYPES = [('numeric', 'Numeric'), ('percentage', 'Percentage'), ('boolean', 'Boolean'), ('currency', 'Currency')]
    PRIORITIES = [('p0', 'P0'), ('p1', 'P1'), ('p2', 'P2'), ('p3', 'P3')]
    RAG_STATUSES = [('green', 'Green'), ('amber', 'Amber'), ('red', 'Red')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='key_results')
    objective = models.ForeignKey(Objective, on_delete=models.CASCADE, related_name='key_results')
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    kr_type = models.CharField(max_length=20, choices=KR_TYPES, default='numeric')
    start_value = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    target_value = models.DecimalField(max_digits=15, decimal_places=4)
    current_value = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    unit = models.CharField(max_length=50, blank=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owned_key_results')
    co_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='co_owned_key_results')
    priority = models.CharField(max_length=5, choices=PRIORITIES, default='p2')
    rag_status = models.CharField(max_length=10, choices=RAG_STATUSES, default='green')
    due_date = models.DateField()
    related_files_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['organization', 'due_date'], name='kr_org_due_idx'),
        ]

    def __str__(self):
        return self.title

class KeyResultHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='key_result_histories')
    key_result = models.ForeignKey(KeyResult, on_delete=models.CASCADE, related_name='history')
    previous_value = models.DecimalField(max_digits=15, decimal_places=4, null=True)
    new_value = models.DecimalField(max_digits=15, decimal_places=4)
    previous_rag_status = models.CharField(max_length=10, blank=True)
    new_rag_status = models.CharField(max_length=10)
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT)
    note = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['organization', 'recorded_at'], name='krh_org_recorded_idx'),
            models.Index(fields=['key_result', 'recorded_at'], name='krh_kr_recorded_idx'),
        ]

class RiskBlocker(models.Model):
    objects = OrganizationManager()
    IMPACT_LEVELS = [('high', 'High'), ('medium', 'Medium'), ('low', 'Low')]
    RAG_STATUSES = [('red', 'Red'), ('amber', 'Amber'), ('green', 'Green')]
    STATUSES = [('open', 'Open'), ('monitoring', 'Monitoring'), ('resolved', 'Resolved')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    key_result = models.ForeignKey(KeyResult, on_delete=models.CASCADE, related_name='risks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    impact = models.CharField(max_length=10, choices=IMPACT_LEVELS)
    rag_status = models.CharField(max_length=10, choices=RAG_STATUSES)
    mitigation_plan = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owned_risks')
    date_identified = models.DateField(auto_now_add=True)
    target_resolution_date = models.DateField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='open')
    logged_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='logged_risks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['organization', 'rag_status'], name='risk_org_rag_idx'),
        ]

class Accomplishment(models.Model):
    objects = OrganizationManager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    key_result = models.ForeignKey(KeyResult, on_delete=models.CASCADE, related_name='accomplishments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    logged_by = models.ForeignKey(User, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class DecisionResource(models.Model):
    objects = OrganizationManager()
    STATUSES = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('deferred', 'Deferred')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    key_result = models.ForeignKey(KeyResult, on_delete=models.CASCADE, related_name='decisions')
    title = models.CharField(max_length=255)
    what_is_needed = models.TextField()
    why_it_matters = models.TextField()
    requested_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='requested_decisions')
    decision_owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owned_decisions')
    date_requested = models.DateField(auto_now_add=True)
    needed_by_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='pending')
    decision_notes = models.TextField(blank=True)
    date_decided = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Notification(models.Model):
    objects = OrganizationManager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    entity_type = models.CharField(max_length=50, blank=True)
    entity_id = models.UUIDField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read'], name='notif_user_read_idx'),
        ]

class AuditLog(models.Model):
    objects = OrganizationManager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    performed_by = models.ForeignKey(User, on_delete=models.PROTECT)
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    previous_state = models.JSONField(null=True)
    new_state = models.JSONField(null=True)
    ip_address = models.GenericIPAddressField(null=True)
    performed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-performed_at']
