
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  EnterpriseViewSet, FacesViewSet

router = DefaultRouter()
enterprise_vieset_router = DefaultRouter()

enterprise_vieset_router.register('', EnterpriseViewSet, basename='enterprise')

urlpatterns = [
    path('employee/add_face/', FacesViewSet.as_view({'post': 'create'}),
         name='Add face to Employee in enterprise'),

    path('employee/<employee_id>/all_pictures/', FacesViewSet.as_view({'get': 'get_all_picture'}),
         name='Get all_picture for Employee in enterprise'),

    path('employee/<picture_id>/destroy/', FacesViewSet.as_view({'delete': 'destroy'}),
         name='delete_picture from employee in enterprise'),

    path('employee/<employee_id>/<picture_id>/get_picture/', FacesViewSet.as_view({'get': 'get_picture_by_id'}),
         name='get picture by id from employee in enterprise'),

    path('employee/<picture_id>/', FacesViewSet.as_view({'put': 'update'}),
         name='Update picture by id from employee in enterprise'),
]

