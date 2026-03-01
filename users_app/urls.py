from django.urls import path
from .views import LoginView, SwitchOrganizationView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/switch-organization/', SwitchOrganizationView.as_view(), name='switch_org'),
]
