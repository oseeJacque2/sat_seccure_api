from django.urls import path, include
from rest_framework.routers import DefaultRouter

from admins.views import  ManageEnterpriseViews, SystemAdminLogin, SystemAdminSendPasswordResetEmailView, AdminUserPasswordResetView, AdminUserChangePasswordView, AdminUserProfileView

from entreprise.views import CountryViewSet

router = DefaultRouter()

#admins_account_router = DefaultRouter()
#admins_account_router.register('', SystemAdminsViews, basename='admins_account')

country_router = DefaultRouter()
country_router.register('', CountryViewSet, basename='country')
admins_management_enterprise = DefaultRouter()
admins_management_enterprise.register('', ManageEnterpriseViews, basename= 'manage enterprise')

urlpatterns = [
    #path("account/", include(admins_account_router.urls)),
    path("manage_enterprise/", include(admins_management_enterprise.urls)),
    path('countries/', include(country_router.urls)),
    path("account/login/", SystemAdminLogin.as_view(), name="Admin login"),
    path("account/forget_password/", SystemAdminSendPasswordResetEmailView.as_view(), name="Admin forget password"),
    path("account/forget_password/verify/<uid>/<token>", AdminUserPasswordResetView.as_view(), name= "Admin verify password"),
    path("account/forget_password/change/", AdminUserChangePasswordView.as_view(), name= "Change password"),
    path('account/me/', AdminUserProfileView.as_view(), name="Admin account information")

]