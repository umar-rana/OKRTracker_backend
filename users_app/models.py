import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    avatar_url = models.URLField(blank=True, null=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Organization(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('suspended', 'Suspended')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    logo_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['slug'], name='org_slug_idx'),
            models.Index(fields=['status'], name='org_status_idx'),
        ]

    def __str__(self):
        return self.name

class Membership(models.Model):
    ROLES = [
        ('platform_admin', 'Platform Admin'),
        ('ceo', 'CEO'),
        ('hr_manager', 'HR Manager'),
        ('team_lead', 'Team Lead'),
        ('member', 'Member'),
        ('read_only', 'Read-Only'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=30, choices=ROLES)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'organization')
        indexes = [
            models.Index(fields=['user', 'organization', 'is_active'], name='mem_user_org_active_idx'),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role})"

class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='led_teams')
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.organization.name})"

class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    email = models.EmailField()
    role = models.CharField(max_length=30)
    token = models.CharField(max_length=255, unique=True)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class EmailSettings(models.Model):
    PROVIDER_GMAIL = 'gmail'
    PROVIDER_SENDGRID = 'sendgrid'
    PROVIDER_AWS_SES = 'aws_ses'
    PROVIDER_CHOICES = [
        (PROVIDER_GMAIL, 'Gmail SMTP'),
        (PROVIDER_SENDGRID, 'SendGrid'),
        (PROVIDER_AWS_SES, 'AWS SES'),
    ]

    organization = models.OneToOneField(
        Organization, on_delete=models.CASCADE, related_name='email_settings'
    )
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default=PROVIDER_GMAIL)
    display_name = models.CharField(max_length=100, default='Argos')
    is_active = models.BooleanField(default=True)

    # Gmail SMTP
    gmail_user = models.EmailField(blank=True, default='')
    gmail_app_password = EncryptedCharField(max_length=500, blank=True, default='')

    # SendGrid
    sendgrid_api_key = EncryptedCharField(max_length=500, blank=True, default='')
    sendgrid_from_email = models.EmailField(blank=True, default='')

    # AWS SES
    aws_access_key_id = EncryptedCharField(max_length=500, blank=True, default='')
    aws_secret_access_key = EncryptedCharField(max_length=500, blank=True, default='')
    aws_region = models.CharField(max_length=50, blank=True, default='us-east-1')
    aws_from_email = models.EmailField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Email Settings'
        verbose_name_plural = 'Email Settings'

    def __str__(self):
        return f"Email Settings for {self.organization.name} ({self.provider})"
