from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnterpriseLoginView, EnterpriseCreateWithoutRegisterView, EnterpriseViewSet, \
    EnterpriseAskValidationView, FacesViewSet, EmployeeViewSet

router = DefaultRouter()
enterprise_vieset_router = DefaultRouter()

enterprise_vieset_router.register('', EnterpriseViewSet, basename='enterprise')

urlpatterns = [
    path('enterprise/<int:enterprise_id>/create/', EmployeeViewSet.as_view({'post': 'create'}), name='Create Employee in enterprise'),
    path('enterprise/<int:interprise_id>/<employee_id>/update/', EmployeeViewSet.as_view({'put': 'update'}),
         name='Update Employee in enterprise'),
    path('enterprise/<interprise_id>/<employee_id>/', EmployeeViewSet.as_view({'get': 'get_employee'}),
         name='Get Employee in enterprise'),
    path('enterprise/<interprise_id>/employee/all/', EmployeeViewSet.as_view({'get': 'get_all_employee_by_enterprize'}),
         name='Get Employee in enterprise'),
    path('enterprise/<interprise_id>/<employee_id>/destroy/', EmployeeViewSet.as_view({'delete': 'destroy'}),
         name='Delete Employee in enterprise'),
    path('enterprise/<interprise_id>/<employee_id>/qr/', EmployeeViewSet.as_view({'get': 'get_employee_qr'}),
         name='get employee code qr'),
    path('enterprise/<interprise_id>/<employee_id>/security_code/', EmployeeViewSet.as_view({'get': 'get_employee_security_code'}),
         name='get employee security code'),
     path('enterprise/<int:enterprise_id>/<int:room_id>/all_employee/',EmployeeViewSet.as_view({"get":'get_employee_by_room_in_enterpise'}))
]
