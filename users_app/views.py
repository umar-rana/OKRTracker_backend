from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Membership, Organization, Team, Invitation
from .serializers import UserSerializer, OrganizationSerializer, MembershipSerializer, MembershipDetailSerializer, TeamSerializer
from .permissions import IsPlatformAdmin, IsCEO, IsHRManager, AtLeastTeamLead, AtLeastCEO

class TrackrTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        membership = user.memberships.filter(is_active=True).first()
        if membership:
            token['org_id'] = str(membership.organization.id)
            token['role'] = membership.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        memberships = self.user.memberships.filter(is_active=True)
        data['memberships'] = MembershipSerializer(memberships, many=True).data
        active_membership = memberships.first()
        if active_membership:
            data['active_organization_id'] = active_membership.organization.id
        return data

class LoginView(TokenObtainPairView):
    serializer_class = TrackrTokenObtainPairSerializer

class SwitchOrganizationView(APIView):
    def post(self, request):
        org_id = request.data.get('organization_id')
        if not org_id:
            return Response({"error": "organization_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        membership = get_object_or_404(Membership, user=request.user, organization_id=org_id, is_active=True)
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(request.user)
        refresh['org_id'] = str(membership.organization.id)
        refresh['role'] = membership.role
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'active_organization_id': membership.organization.id
        })

class MembershipViewSet(viewsets.ModelViewSet):
    serializer_class = MembershipDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsHRManager]

    def get_queryset(self):
        org_id = self.request.auth.get('org_id')
        return Membership.objects.filter(organization_id=org_id)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsHRManager])
    def invite(self, request):
        email = request.data.get('email')
        role = request.data.get('role', 'member')
        org_id = request.auth.get('org_id')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        import secrets
        from django.utils import timezone
        from datetime import timedelta
        invitation = Invitation.objects.create(
            organization_id=org_id,
            email=email,
            role=role,
            token=secrets.token_urlsafe(32),
            invited_by=request.user,
            expires_at=timezone.now() + timedelta(days=7)
        )
        from .email_utils import send_trackr_email
        send_trackr_email(
            invitation.organization,
            f"You're invited to join {invitation.organization.name} on Argos",
            f"Hi there,\n\nYou have been invited to join {invitation.organization.name} on Argos as a {role}.\n\nClick here to accept: {settings.FRONTEND_URL}/accept-invitation?token={invitation.token}\n\nThis link expires in 72 hours.",
            email
        )
        return Response({"message": f"Invitation sent to {email}"})

class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated, AtLeastTeamLead]

    def get_queryset(self):
        org_id = self.request.auth.get('org_id')
        return Team.objects.filter(organization_id=org_id)

    def perform_create(self, serializer):
        org_id = self.request.auth.get('org_id')
        serializer.save(organization_id=org_id)

class AcceptInvitationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        if not token or not password:
            return Response({"error": "Token and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        from django.utils import timezone
        invitation = get_object_or_404(Invitation, token=token, used_at__isnull=True)
        
        if invitation.expires_at < timezone.now():
            return Response({"error": "Invitation has expired"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Create or get user
        from .models import User
        user, created = User.objects.get_or_create(
            email=invitation.email,
            defaults={
                'username': invitation.email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        
        if created:
            user.set_password(password)
            user.save()

        # 2. Create membership
        Membership.objects.get_or_create(
            user=user,
            organization=invitation.organization,
            defaults={'role': invitation.role}
        )

        # 3. Mark invitation as used
        invitation.used_at = timezone.now()
        invitation.save()

        # 4. Send Welcome Email
        from .email_utils import send_trackr_email
        send_trackr_email(
            invitation.organization,
            "Welcome to Argos!",
            f"Hi {user.first_name or user.email},\n\nWelcome to {invitation.organization.name} on Argos! You can now login at {settings.FRONTEND_URL}/login",
            user.email
        )

        return Response({"message": "Invitation accepted successfully. You can now login."}, status=status.HTTP_201_CREATED)

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsPlatformAdmin]

    def get_queryset(self):
        if self.request.auth and self.request.auth.get('role') == 'platform_admin':
            return Organization.objects.all()
        return Organization.objects.none()

from .models import EmailSettings
from .serializers import EmailSettingsSerializer

class EmailSettingsViewSet(viewsets.GenericViewSet):
    serializer_class = EmailSettingsSerializer
    permission_classes = [permissions.IsAuthenticated, AtLeastCEO]

    def get_object(self):
        org_id = self.request.auth.get('org_id')
        obj, created = EmailSettings.objects.get_or_create(organization_id=org_id)
        return obj

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def test(self, request):
        instance = self.get_object()
        from .email_utils import send_trackr_email
        try:
            success = send_trackr_email(
                instance.organization,
                "Argos Email Connection Test",
                "If you are reading this, your email configuration on Argos is working correctly!",
                request.user.email
            )
            if success:
                return Response({"detail": f"Test email sent successfully to {request.user.email}"})
            else:
                return Response({"detail": "Failed to send test email. Check your provider logs."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
