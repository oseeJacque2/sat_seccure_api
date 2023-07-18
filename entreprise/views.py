from django.contrib.auth.hashers import check_password
from django.db.migrations import serializer
from rest_framework import viewsets, status
from rest_framework.decorators import authentication_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from .models import Country, Enterprise, EnterpriseAdmin
from .serializers import CountrySerializer, EnterpriseSerializer, EnterpriseCreateSerializerWithoutRegister, \
    EnterpriseUpdateSerializer

from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny

from account.models import User
from account.serializers import UserLoginSerializer
from account.views import get_tokens_for_user


############################## Enterprise View #########################################"

#Enterprise register when the user has account on our system
class EnterpriseRegisterViewSet(APIView):
    """
    This view is use when the user is connected on our system
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EnterpriseSerializer
    queryset = Enterprise.objects.all()
    @swagger_auto_schema(
        operation_description="Create entreprise",
        request_body=EnterpriseSerializer
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



# Create entreprise without user account in first step
@authentication_classes([])
class EnterpriseCreateWithoutRegisterView(APIView):
    """
    This view use to creae Entreprise without user has account on the system
    """
    serializer_classs = EnterpriseCreateSerializerWithoutRegister
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="",
        request_body=EnterpriseCreateSerializerWithoutRegister
    )
    def post(self, request, *args, **kwargs):
        serializer = EnterpriseCreateSerializerWithoutRegister(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")
        password = serializer.data.get("password")
        users = User.objects.get(email=email)
        if users is not None:
            return Response({'msg': "This email has already used"}, status=status.HTTP_404_NOT_FOUND)
        else:
            #Create User
            user = serializer.save()
            if user is not None:
                token = get_tokens_for_user(user)
                #Create Enterprise
                name = serializer.data.get("name")
                entreprise = Enterprise(name=name,)
                entreprise.save()

                #Create Entreprise admin
                entrepriseAdmin = EnterpriseAdmin(user=user, is_creator=True)
                entrepriseAdmin.save()
                return Response({"token": token, "msg": "Registration successful"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

######################## Update enterprise ####################################################
class EnterpriseUpdatedView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EnterpriseUpdateSerializer

    @swagger_auto_schema(
        operation_description="Auth_entreprise_login",
        request_body=EnterpriseUpdateSerializer

    )

    def post(self, request):
        enterprisesAdmins = EnterpriseAdmin.objects.all()
        current_user = request.user
        serializer = self.EnterpriseUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for enterprise_admin in enterprisesAdmins:
            if enterprise_admin.user == current_user.id:
                if enterprise_admin.is_creator:
                    enterprise = serializer.update(enterprise_admin.enterprise, serializer.validated_data)
                    return Response({"msg": "Enterprise modified success", "enterprise": enterprise}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"msg": "You do not have the permission"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"msg": "Enterprise admin not found"}, status=status.HTTP_400_BAD_REQUEST)



class EnterpriseLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    @swagger_auto_schema(
        operation_description="Auth_entreprise_login",
        request_body=UserLoginSerializer
    )
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = User.objects.get(email=email)
        print(user)

        if user is not None:
            if check_password(password, user.password):
                entrepriseAdmin = EnterpriseAdmin.objects.get(id=user.id)
                print(entrepriseAdmin)
                if entrepriseAdmin.id != 0:
                    token = get_tokens_for_user(user)
                    print(user.password)
                    return Response({'token': token, 'msg': 'Login Sucess'}, status=status.HTTP_200_OK)
                else:
                    return  Response({'msg':'You are not any entreprise admin'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}},
                        status=status.HTTP_404_NOT_FOUND)


class EnterpriseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EnterpriseSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    @swagger_auto_schema(
        operation_description="Create entreprise",
        request_body=EnterpriseSerializer
    )
    def create(self, request, *args, **kwargs):
        user = request.user
        print(f"l'utilisateur est {user.name}")
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            #Create enterprise admin
            enterprise_admin = EnterpriseAdmin.objects.get(user=user.id)
            if enterprise_admin is not None:
                serializer.data.update(user=user)
                enterprise = serializer.save()
                enterprise_admin.enterprises.add(enterprise)
                enterprise_admin.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                enterprise = serializer.save()
                new_entrepriseAdmin = EnterpriseAdmin(user=user)
                new_entrepriseAdmin.enterprises.add(enterprise)
                new_entrepriseAdmin.save()
                Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #Upadate enterprise
    def update(self, request, pk=None, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance, data=request.data, partial=True)
        if serializer.is_valid():
            if instance.creator.id == user.id:
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    #@action(detail=True, methods=["delete"], url_path=r'delete-enterprise',)
    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        user = request.user

        # Verification if the current user has the right to delete the enterprise
        if instance.creator.id != user.id:
            return Response(data="Vous n'êtes pas autorisé à supprimer cet objet.", status=status.HTTP_403_FORBIDDEN)

        instance.delete()  # Suppression de l'objet Enterprise
        return Response(data="L'entreprise a été supprimée avec succès.", status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, pk=None):
        user = request.user
        instance = self.get_object()
        if instance.creator.id != user.id:
            return Response(data="Vous n'êtes pas  à lire les données liées   l'entreprise .", status=status.HTTP_403_FORBIDDEN)
        # query = request.GET.get('query', None)  # read extra data
        return Response(self.serializer_class(instance).data,
                        status=status.HTTP_200_OK)

    #@action(detail=False, methods=["get"], url_path=r'list-enterprise', )
    def get_queryset(self):
        self.queryset = Enterprise.objects.all()
        return self.queryset









    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


################################## Viewset for Country #########################################""
@swagger_auto_schema(
        operation_description="Create country",
        request_body=CountrySerializer
    )
class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminUser]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)