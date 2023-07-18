from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CountryViewSet,  EnterpriseLoginView, EnterpriseCreateWithoutRegisterView

urlpatterns = [
    path('login/', EnterpriseLoginView.as_view()),
    path('registerbase/', EnterpriseCreateWithoutRegisterView.as_view(), name='Create entreprise without having account')
]
