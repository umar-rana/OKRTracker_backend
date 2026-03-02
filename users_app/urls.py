from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, SwitchOrganizationView, MembershipViewSet, TeamViewSet
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'members', MembershipViewSet, basename='membership')
router.register(r'teams', TeamViewSet, basename='team')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/switch-organization/', SwitchOrganizationView.as_view(), name='switch_org'),
    path('orgs/<uuid:orgId>/users/', include(router.urls)),
]
