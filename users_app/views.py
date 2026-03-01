from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Membership, Organization
from .serializers import UserSerializer, MembershipSerializer

class TrackrTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        # Default to the first active organization membership
        membership = user.memberships.filter(is_active=True).first()
        if membership:
            token['org_id'] = str(membership.organization.id)
            token['role'] = membership.role
            
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user info and memberships to response
        data['user'] = UserSerializer(self.user).data
        memberships = self.user.memberships.filter(is_active=True)
        data['memberships'] = MembershipSerializer(memberships, many=True).data
        
        # Set active organization in response
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
        
        # Generate new token with updated org_id
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(request.user)
        refresh['org_id'] = str(membership.organization.id)
        refresh['role'] = membership.role
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'active_organization_id': membership.organization.id
        })
