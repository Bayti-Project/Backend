from django.urls import path

from .views import RegisterView, LoginView, ProfileView, ChangePasswordView, LogoutView
from .owner_profile_views import OwnerProfileView
from .tenant_profile_views import TenantProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('owner/profile/', OwnerProfileView.as_view(), name='owner-profile'),
    path('tenant/profile/', TenantProfileView.as_view(), name='tenant-profile'),
]
