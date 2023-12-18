from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnterpriseLoginView, EnterpriseCreateWithoutRegisterView, EnterpriseViewSet, \
    EnterpriseAskValidationView,CompleteEnterpriseInformationView, download_face_file

router = DefaultRouter()
enterprise_vieset_router = DefaultRouter()

enterprise_vieset_router.register('', EnterpriseViewSet, basename='enterprise')

urlpatterns = [
    #path('login/', EnterpriseLoginView.as_view()),
    path('registerbase/', EnterpriseCreateWithoutRegisterView.as_view(), name='Create entreprise without having account'),
    path('', include(enterprise_vieset_router.urls)),
    path('validation/<pk>/', EnterpriseAskValidationView.as_view({'post': 'enterprise_validation'}), name="Ask validation enterprise"),
    path('<enterprise_id>/rooms/', EnterpriseViewSet.as_view({'get': 'get_room_for_enterprise'}), name= "Get rooms for enterprises"),
    path('complete_infor/<enterprise_id>/', CompleteEnterpriseInformationView.as_view(), name="complete_enterprise_information"),
    path('download-face-file/<int:face_id>/', download_face_file, name='download-face-file'),


]
