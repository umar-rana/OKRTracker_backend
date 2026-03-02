from django.core.mail import get_connection
from django.core.mail.message import EmailMessage
from .models import EmailSettings
import logging

logger = logging.getLogger(__name__)

def get_email_connection(organization):
    try:
        settings = EmailSettings.objects.get(organization=organization, is_active=True)
        
        if settings.provider == EmailSettings.PROVIDER_GMAIL:
            return get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                host='smtp.gmail.com',
                port=587,
                username=settings.gmail_user,
                password=settings.gmail_app_password,
                use_tls=True,
            ), settings.display_name, settings.gmail_user
            
        elif settings.provider == EmailSettings.PROVIDER_SENDGRID:
            return get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                host='smtp.sendgrid.net',
                port=587,
                username='apikey',
                password=settings.sendgrid_api_key,
                use_tls=True,
            ), settings.display_name, settings.sendgrid_from_email
            
        elif settings.provider == EmailSettings.PROVIDER_AWS_SES:
            # Note: AWS SES usually requires specific django-ses or custom backend
            # For simplicity, we'll assume SMTP interface for SES as well
            return get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                host=f'email-smtp.{settings.aws_region}.amazonaws.com',
                port=587,
                username=settings.aws_access_key_id,
                password=settings.aws_secret_access_key,
                use_tls=True,
            ), settings.display_name, settings.aws_from_email
            
    except EmailSettings.DoesNotExist:
        logger.warning(f"No active email settings found for organization {organization.name}. Falling back to default.")
    except Exception as e:
        logger.error(f"Error configuring email for {organization.name}: {str(e)}")

    return get_connection(), "Trackr", None

def send_trackr_email(organization, subject, body, to_email):
    connection, from_name, from_email = get_email_connection(organization)
    
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=f"{from_name} <{from_email or 'noreply@trackr.app'}>",
        to=[to_email],
        connection=connection
    )
    return email.send()
