from rest_framework import serializers
from .models import User, Organization, Membership

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug', 'logo_url']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'avatar_url']

class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ['organization', 'role', 'is_active']

class MembershipDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = Membership
        fields = ['id', 'user', 'organization', 'organization_name', 'role', 'is_active', 'joined_at']

from .models import Team

class TeamSerializer(serializers.ModelSerializer):
    lead_details = UserSerializer(source='lead', read_only=True)
    member_details = UserSerializer(source='members', many=True, read_only=True)
    
    class Meta:
        model = Team
        fields = ['id', 'organization', 'name', 'description', 'lead', 'lead_details', 'members', 'member_details', 'created_at']
