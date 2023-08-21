"""
URL configuration for swanapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter


from entreprise.views import EnterpriseViewSet, EmployeeViewSet, RoomViewset,EmployeeRoomViewset,QrViewset, SecurityCodeViewset, EnterpriseAdminRoleViewSet, EnterpriseAdminViewSet


...

enterprise_router = DefaultRouter()
enterprise_router.register(r'entreprise', EnterpriseViewSet, basename='Entreprise')

employee_router =DefaultRouter()
room_router = DefaultRouter()
room_router.register(r"enterprise", RoomViewset, basename="enterprise Room")

employee_room_router = DefaultRouter()
employee_room_router.register(r"employee", EmployeeRoomViewset, basename="Employee room")

qr_router = DefaultRouter()
qr_router.register(r"employee", QrViewset, basename="Code Qr")

SecurityCode_router = DefaultRouter()
SecurityCode_router.register(r"employee", SecurityCodeViewset, basename="Employee Security Code")

Employee_router = DefaultRouter()
Employee_router.register(r"enterprise", EmployeeViewSet, basename="Security Code")

EnterpriseAdminRole_router = DefaultRouter()
EnterpriseAdminRole_router.register(r"Enterprise", EnterpriseAdminRoleViewSet, basename="EnterpriseAdminRole")

EnterpriseAdmin_router = DefaultRouter()
EnterpriseAdmin_router.register(r"Enterprise",     EnterpriseAdminViewSet, basename="EnterpriseAdmin")



schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    #app urls
    path("auth/", include("account.urls"), name="User Account"),
    path('enterprise/', include("entreprise.urls"), name="Enterpise"),
    path('admins/', include("admins.urls"), name="Admins"),
    path('face/', include("entreprise.faces_urls"), name="Faces"),

    #Goupe urls
    path('employee/', include("entreprise.employee_urls"), name="Employee"),
    #path('employee/', include(Employee_router.urls), name="Security Code"),
    path('room/', include(room_router.urls), name="Rooms"),
    path('employee_room/', include(employee_room_router.urls), name="Employee room"),
    path('qr/', include(qr_router.urls), name="Qr"),
    path('security_Code/', include(SecurityCode_router.urls), name="Security Code"),
    path('enterprise_admin_role/', include(EnterpriseAdminRole_router.urls), name="Enterprise Admin Role"),
    path('enterprise_admin/', include(EnterpriseAdmin_router.urls), name="Enterprise Admin "),

]
