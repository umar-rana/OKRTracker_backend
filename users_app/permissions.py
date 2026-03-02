from rest_framework import permissions

class BaseRolePermission(permissions.BasePermission):
    required_roles = []

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        role = request.auth.get('role')
        if not role:
            return False
            
        return role in self.required_roles

class IsPlatformAdmin(BaseRolePermission):
    required_roles = ['platform_admin']

class IsCEO(BaseRolePermission):
    required_roles = ['ceo', 'platform_admin']

class IsHRManager(BaseRolePermission):
    required_roles = ['hr_manager', 'ceo', 'platform_admin']

class IsTeamLead(BaseRolePermission):
    required_roles = ['team_lead', 'ceo', 'platform_admin']

class IsMember(BaseRolePermission):
    required_roles = ['member', 'team_lead', 'ceo', 'platform_admin']

class IsReadOnly(BaseRolePermission):
    required_roles = ['read_only', 'member', 'team_lead', 'ceo', 'platform_admin']

class AtLeastTeamLead(BaseRolePermission):
    required_roles = ['team_lead', 'ceo', 'platform_admin']

class AtLeastCEO(BaseRolePermission):
    required_roles = ['ceo', 'platform_admin']
