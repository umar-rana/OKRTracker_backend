from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, SwitchOrganizationView, MembershipViewSet, TeamViewSet, AcceptInvitationView, OrganizationViewSet
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'members', MembershipViewSet, basename='membership')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'admin/organizations', OrganizationViewSet, basename='organization')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/switch-organization/', SwitchOrganizationView.as_view(), name='switch_org'),
    path('auth/accept-invitation/', AcceptInvitationView.as_view(), name='accept_invitation'),
    path('orgs/<uuid:orgId>/users/', include(router.urls)),
]
