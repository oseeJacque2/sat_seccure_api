from django.contrib.auth.hashers import check_password
from django.db.migrations import serializer
from rest_framework import viewsets, status, parsers
from rest_framework.decorators import authentication_classes, action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.db import models

from .models import Country, Enterprise, EnterpriseAdmin, Employee, Face, Room, EmployeeRoom, Qr, SecurityCode, \
    EnterpriseAdminRole
from .serializers import CountrySerializer, EnterpriseSerializer, EnterpriseCreateSerializerWithoutRegister, \
    EnterpriseUpdateSerializer, EnterpriseValidationSerializer, EntrepriseAdminSerializer, EnterpriseCreateSerializer, \
    EmployeeSerializer, CreateEmployeeSerializer, UpdateEmployeeSerializer, FacesSerializer, RoomSerializer, \
    EmployeeRoomSerializer, QrSerializer, SecurityCodeSerializer, EnterpriseAdminRoleSerializer

from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny

from account.models import Custom_User
from account.serializers import UserLoginSerializer
from account.views import get_tokens_for_user

from admins.models import SystemAdmin


############################## Enterprise View #########################################"


# Create entreprise without user account in first step
@authentication_classes([])
class EnterpriseCreateWithoutRegisterView(APIView):
    """
    This view use to creae Entreprise without user has account on the system
    """
    serializer_classs = EnterpriseCreateSerializerWithoutRegister
    permission_classes = [AllowAny]
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

    @swagger_auto_schema(
        operation_description="",
        request_body=EnterpriseCreateSerializerWithoutRegister
    )
    def post(self, request, *args, **kwargs):
        serializer = EnterpriseCreateSerializerWithoutRegister(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")
        password = serializer.data.get("password")
        users = Custom_User.objects.get(email=email)
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


class EnterpriseLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

    @swagger_auto_schema(
        operation_description="Auth_entreprise_login",
        request_body=UserLoginSerializer
    )
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = Custom_User.objects.get(email=email)
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
                    return Response({'msg': 'You are not any entreprise admin'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}},
                        status=status.HTTP_404_NOT_FOUND)


class EnterpriseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EnterpriseCreateSerializer
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

    def get_queryset(self):
        self.queryset = Enterprise.objects.all()
        return self.queryset

    def get_serializer_class(self):
        if self.action == "retrieve" or self.action == "list":
            return EnterpriseSerializer
        else:
            return self.serializer_class

    #def list(self, request):
        #return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    def list(self, request):
        queryset = Enterprise.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer. data)

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                enterprise_admin = EnterpriseAdmin.objects.get(user=user)
                serializer.validated_data['creator_id'] = user.id
                enterprise = serializer.save()
                enterprise_admin.enterprises.add(enterprise)
                enterprise_admin.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except EnterpriseAdmin.DoesNotExist:
                serializer.validated_data['creator_id'] = user.id
                enterprise = serializer.save()
                new_enterprise_admin = EnterpriseAdmin(user=user)
                new_enterprise_admin.save()
                new_enterprise_admin.enterprises.add(enterprise)

                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk=None, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data, partial=True)
        if serializer.is_valid():
            if instance.creator.id == user.id:
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        user = request.user
        print(user)
        instance = self.get_object()
        if instance.creator.id != user.id:
            print(f"Vous n'êtes pas le créateur")
            return Response(data="You have not acces to data from enterprise", status=status.HTTP_403_FORBIDDEN)
        return Response(self.serializer_class(instance).data,
                        status=status.HTTP_200_OK)
    def get_room_for_enterprise(self, request, pk=None, *args, **kwargs):
        user = request.user
        id = self.kwargs.get("enterprise_id")
        enterprise = get_object_or_404(Enterprise, id=id)
        rooms = Room.objects.filter(enterprise=enterprise)
        return Response(RoomSerializer(rooms, many=True).data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if instance.creator.id != user.id:
            return Response(data="You have not permission to delete enterprise", status=status.HTTP_403_FORBIDDEN)

        instance.delete()  # Suppression de l'objet Enterprise
        return Response(data="Enterprise deleted succes", status=status.HTTP_204_NO_CONTENT)



class EnterpriseAskValidationView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EnterpriseValidationSerializer
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

    def get_queryset(self):
        self.queryset = Enterprise.objects.all()
        return self.queryset


    @action(detail=True, methods=["post"])
    def enterprise_validation(self, request, pk=None, *args, **kwargs):
        user = request.user
        print(user)
        try:
            instance = self.get_object() # Récupérer l'instance de l'entreprise correspondant au pk
            serializer = self.get_serializer(instance=instance, data=request.data)

            if serializer.is_valid():
                if instance.creator.id == user.id:
                    serializer.validated_data['is_approved'] = False
                    serializer.save()
                    return Response(data=serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(data="Enterprise is not found",
                            status=status.HTTP_404_NOT_FOUND)

################################# Employee viewset ############################################


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    queryset = Enterprise.objects.all()
    user_employee = Custom_User()

    def get_queryset(self):
        if self.action == "create":
            return self.queryset
        elif self.action == "add_face"  or self.action == "get_all_picture":
            self.queryset = Face.objects.all()
        else:
            self.queryset = Custom_User.objects.all()
            return self.queryset

    def get_serializer_class(self):
        if self.action == "create":
            return CreateEmployeeSerializer
        elif self.action == "update":
            return UpdateEmployeeSerializer
        elif self.action == "add_face" or self.action == "get_all_picture":
            return FacesSerializer
        elif self.action =="get_employee_qr":
            return QrSerializer
        elif self.action == "get_employee_security_code":
            return SecurityCodeSerializer
        else:
            return self.serializer_class

    def create(self, request, *args, **kwargs):
        request_email = request.data.get("email")
        id = self.kwargs.get("enterprise_id")

        try:
            enterprise = get_object_or_404(Enterprise, id=id)
        except Enterprise.DoesNotExist:
            return Response({"error": "Enterprise no found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            self.user_employee = Custom_User.objects.get(email=request_email)
        except Custom_User.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.user_employee = serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        employee = Employee(user=self.user_employee, is_active=False, enterprise=enterprise)
        employee.save()

        return Response({"user": f"{self.user_employee}", "Enterprise": f"{EnterpriseSerializer(enterprise).data}"},
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        user = request.user
        try:
            interprise_id = self.kwargs.get("interprise_id")  # Utilisation des paramètres d'URL
            employee_id = self.kwargs.get("employee_id")  # Utilisation des paramètres d'URL
            employee = Employee.objects.get(id=employee_id)
            instance = Custom_User.objects.get(id=employee.user.id)
            serializer = self.get_serializer(instance=instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"Message": "Employee update success"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True,methods=['get'])
    def get_employee(self, request, *args, **kwargs):
        try:
            interprise_id = self.kwargs.get("interprise_id")
            employee_idd = self.kwargs.get("employee_id")

            employee = Employee.objects.get(enterprise__id=interprise_id, user__id=employee_idd)
            return Response(self.serializer_class(employee).data, status=status.HTTP_200_OK)

        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def get_all_employee_by_enterprize(self, request, *args, **kwargs):
        try:
            interprise_id = self.kwargs.get("interprise_id")
            employees = Employee.objects.filter(enterprise=interprise_id)
            return Response(self.serializer_class(employees,many=True).data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def destroy(self, request, *args, **kwargs):
        user = request.user
        try:
            interprise_id = self.kwargs.get("interprise_id")
            employee_id = self.kwargs.get("employee_id")
            employee = get_object_or_404(Employee, id=employee_id, enterprise__id=interprise_id)
            employee.user.delete()
            employee.delete()
            return Response({"message": "Employee deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @action(detail=True,methods=['get'])
    def get_employee_qr(self, request, *args, **kwargs):
        try:
            user = request.user
            interprise_id = self.kwargs.get("interprise_id")
            employee_id = self.kwargs.get("employee_id")
            employee = Employee.objects.get(enterprise=interprise_id, id=employee_id)
            employee_qr = Qr.objects.filter(employee=employee)
            return Response(self.get_serializer(employee_qr, many=True).data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def get_employee_security_code(self, request, *args, **kwargs):
        try:
            user = request.user
            interprise_id = self.kwargs.get("interprise_id")
            employee_idd = self.kwargs.get("employee_id")

            employee = Employee.objects.get(enterprise__id=interprise_id, user__id=employee_idd)
            print(employee)
            print("Je suis ici")
            employee_qr = SecurityCode.objects.filter(employee=employee_idd)
            print(employee_qr)
            return Response(self.get_serializer(employee_qr, many=True).data, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


########################################## Face viewset #######################################
class FacesViewSet(viewsets.ModelViewSet):
    serializer_class = FacesSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    queryset = Face.objects.all()


    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            employee_id = request.data.get("employee")
            all_image_for_employee = Face.objects.filter(employee=employee_id)
            if all_image_for_employee.exists():
                request.data["is_main"] = False
            else:
                request.data["is_main"] = True
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                print("Serializer is valide")
                serializer.save()
                return Response({"success": "Image added successfully"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    def get_picture_by_id(self, request, *args, **kwargs):
        user = request.user
        try:
            picture_id = self.kwargs.get("picture_id")
            employee_id = self.kwargs.get("employee_id")
            image_for_employee = Face.objects.get(id=picture_id)
            print(image_for_employee)
            serializer = self.serializer_class(image_for_employee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    def get_all_picture(self, request, *args, **kwargs):
        user = request.user
        try:
            interprise_id = self.kwargs.get("interprise_id")
            employee_id = self.kwargs.get("employee_id")
            all_image_for_employee = Face.objects.filter(employee=employee_id)
            serializer = self.get_serializer(all_image_for_employee, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
    def update(self, request, *args, **kwargs):
        user = request.user
        try:
            picture_id = self.kwargs.get("picture_id")
            print(picture_id)
            employee = self.kwargs.get("employee")
            print(employee)
            instance = Face.objects.get(id=picture_id)
            print(instance)
            serializer = self.serializer_class(instance=instance, data=request.data)
            print("'m on it'")
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.error_messages,status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f'{e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def destroy(self, request, *args, **kwargs):
        user = request.user
        try:
            picture_id = self.kwargs.get("picture_id")
            employee_id = self.kwargs.get("employee_id")
            print("We are here")
            picture_for_user = get_object_or_404(Face,id=picture_id)
            picture_for_user.delete()
            return Response({"msg": "Image delete successfully"})
        except Exception as e:
            return Response({"error": f"Face for this id no found"},status=status.HTTP_404_NOT_FOUND)


############################################# Enterprise Room  Viewset ########################

class RoomViewset(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    queryset = Room.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


#####################################  EmployeeRoom ###########################################
class EmployeeRoomViewset(viewsets.ModelViewSet):
    serializer_class = EmployeeRoomSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    queryset = EmployeeRoom.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": f"{serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)



######################################## Qr visewset ##########################################
class QrViewset(viewsets.ModelViewSet):
    serializer_class = QrSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    queryset = Qr.objects.all()

    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": f"{serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"{e}"},status=status.HTTP_400_BAD_REQUEST)

######################################SecurityCode Viewset ####################################
class SecurityCodeViewset(viewsets.ModelViewSet):
    serializer_class = SecurityCodeSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    queryset = SecurityCode.objects.all()

    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": f"{serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"{e}"},status=status.HTTP_400_BAD_REQUEST)
################################## Viewset for Country ########################################

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminUser]
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

#########################################  Rôle Serializer #####################################
class EnterpriseAdminRoleViewSet(viewsets.ModelViewSet):
    queryset = EnterpriseAdminRole.objects.all()
    serializer_class = EnterpriseAdminRoleSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)


#########################################  EnterpriseAdmin Serializer #####################################
class EnterpriseAdminViewSet(viewsets.ModelViewSet):
    queryset = EnterpriseAdmin.objects.all()
    serializer_class = EntrepriseAdminSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
