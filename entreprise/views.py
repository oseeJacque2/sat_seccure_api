from django.contrib.auth.hashers import check_password
from django.db.migrations import serializer
from django.http import HttpResponse
from rest_framework import viewsets, status, parsers
from rest_framework.decorators import authentication_classes, action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.db import models
from django.urls import reverse
from django.core.files.base import ContentFile
from io import BytesIO
import qrcode
from urllib.parse import urljoin
from swan_project import settings

from .models import Country, EconomicSector, Enterprise, EnterpriseAdmin, Employee, Face, Room, EmployeeRoom, Qr, SecurityCode, \
    EnterpriseAdminRole
from .serializers import AddEnterpriseDocumentsSerializer, CompletEnterpiseInformationSerializer, CountrySerializer, EconomicSectorSerializer, EnterpriseSerializer, EnterpriseCreateSerializerWithoutRegister, \
    EnterpriseUpdateSerializer, EnterpriseValidationSerializer, EntrepriseAdminSerializer, EnterpriseCreateSerializer, \
    EmployeeSerializer, CreateEmployeeSerializer, UpdateEmployeeSerializer, FacesSerializer, RoomSerializer, \
    EmployeeRoomSerializer, QrSerializer, SecurityCodeSerializer, EnterpriseAdminRoleSerializer

from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny

from account.models import Custom_User
from account.serializers import UserLoginSerializer
from account.views import get_tokens_for_user

from admins.models import SystemAdmin

def download_face_file(request, face_id):
    face = get_object_or_404(Face, id=face_id)
    file_url = reverse('download-face-file', kwargs={'face_id': face_id})
    file_path = settings.MEDIA_ROOT + face.face_file.name  # Ajuster selon votre configuration
    with open(file_path, 'rb') as file:
        response = HttpResponse(file.read())
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment; filename="{face.face_file.name}"'
        return response
    
    
############################## Enterprise View #########################################"


# Create entreprise without user account in first step
@authentication_classes([])
class EnterpriseCreateWithoutRegisterView(APIView):
    """
    This view use to creae Entreprise without user has account on the system
    """
    serializer_classs = EnterpriseCreateSerializerWithoutRegister
    permission_classes = [AllowAny]
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

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

################################################ Complete Enterprise information view ########################################"" 

class CompleteEnterpriseInformationView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompletEnterpiseInformationSerializer
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    
    @swagger_auto_schema(
        operation_description="Auth_entreprise_login",
        request_body=CompletEnterpiseInformationSerializer
    ) 
  
    def post(self, request, enterprise_id, *args, **kwargs):
        try:
            enterprise = Enterprise.objects.get(pk=enterprise_id)
        except Enterprise.DoesNotExist:
            return Response({"error": "Enterprise not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompletEnterpiseInformationSerializer(instance=enterprise, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Enterprise information updated successfully", "enterprise": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class AddEnterpriseDocumentsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddEnterpriseDocumentsSerializer
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    
    @swagger_auto_schema(
        operation_description="Add documents  for Enterprise ",
        request_body=AddEnterpriseDocumentsSerializer
    ) 
    def post(self, request, enterprise_id, *args, **kwargs):
        try:
            enterprise = Enterprise.objects.get(pk=enterprise_id)
        except Enterprise.DoesNotExist:
            return Response({"error": "Enterprise not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = AddEnterpriseDocumentsSerializer(instance=enterprise, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Enterprise information updated successfully", "enterprise": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        
    
class EnterpriseLoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

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
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

    def get_queryset(self):
        self.queryset = Enterprise.objects.all()
        return self.queryset

    def get_serializer_class(self):
        if self.action == "retrieve" or self.action == "list" or self.action == "" or self.action == "update":
            return EnterpriseSerializer 
        
        else:
            return self.serializer_class

    
    def list(self, request):
        user_enterprises = Enterprise.objects.filter(creator=request.user)
        serializer = EnterpriseSerializer(user_enterprises, many=True)
        return Response({"enterprise":serializer.data, "msg": "success"}, status=status.HTTP_200_OK) 

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
                return Response({"enterprise":serializer.data,"msg":"updated success"}, status=status.HTTP_201_CREATED)
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
        return Response({"enterprisen":EnterpriseSerializer(instance).data,"msg":"sucess"},
                        status=status.HTTP_200_OK)
        
    def get_room_for_enterprise(self, request, pk=None, *args, **kwargs):
        user = request.user
        id = self.kwargs.get("enterprise_id")
        enterprise = get_object_or_404(Enterprise, id=id)
        rooms = Room.objects.filter(enterprise=enterprise)
        return Response({"rooms":RoomSerializer(rooms, many=True).data,"msg":"success"}, status=status.HTTP_200_OK)

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
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
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

        return Response({"employee": employee.id, "Enterprise": f"{EnterpriseSerializer(enterprise).data}","msg":"success"},
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
            employee_data = [] 
            for employee in employees:
                #Get enterprise for employee
                user = Custom_User.objects.get(id = employee.user.id)
                enterpise_serializer = EnterpriseSerializer(employee.enterprise)
                #get user images
                all_image_for_employee = Face.objects.filter(employee=employee.id)
                
                # Serialize faces with download URLs
                serialized_faces = []
                for face in all_image_for_employee:
                    face_data = FacesSerializer(face).data
                    face_data['face_file'] = urljoin(request.build_absolute_uri(), face.face_file.url)
                    serialized_faces.append(face_data)
                    
                # Get security code for the employee
                try:
                    employee_security_code = SecurityCode.objects.get(employee=employee.id, is_current=True)
                    security_code_data = SecurityCodeSerializer(employee_security_code).data
                except SecurityCode.DoesNotExist:
                    # If no security code is found, set security_code_data to 0
                    security_code_data = 0    
                    
                #Get qr code 
                try:
                    qr_code = Qr.objects.get(employee=employee.id, is_current=True)
                    qr_code_data = QrSerializer(qr_code).data 
                    qr_code_data["qr_image"] = urljoin(request.build_absolute_uri(), qr_code.qr_image.url)
                except Qr.DoesNotExist:
                    # If no security code is found, set security_code_data to 0
                    qr_code_data = {} 
                
                #Get employee room 
                employeeRooms_data = []
                try:
                    employeeRooms = EmployeeRoom.objects.filter (employee = employee.id)
                    for employeeRoom in employeeRooms:
                        employee_room_serializer = EmployeeRoomSerializer(employeeRoom)
                        employeeRooms_data.append(employee_room_serializer.data)
                except EmployeeRoom.DoesNotExist:
                    employeeRooms_data = [] 
                    
                    
                user_data = {
                    "user":{
                    'id':user.id,
                    'email':user.email,
                    'lastname':user.lastname,
                    'name':user.name,
                    'firstname':user.firstname,
                    'username':user.username,
                    'sexe':user.sexe,
                    'telephone':user.telephone,
                    'picture': str(user.picture),
                    'birth_date':user.birth_date,
                    'adresse':user.adresse,
                    'description':user.description,
                    'profession':user.profession, 
                    },
                    "id": employee.id,
                    "is_active": employee.is_active,
                    "date_created_at" : employee.date_created_at, 
                    "date_updated_at" : employee.date_updated_at,
                    "enterprise": enterpise_serializer.data, 
                    "faces": serialized_faces, 
                    "security_code": security_code_data, 
                    "qr_code":qr_code_data,
                    "rooms": employeeRooms_data
                } 
                
                employee_data.append(user_data) 
            return Response({"employees":employee_data,"msg":"success"}, status=status.HTTP_200_OK)
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
    
    @action(detail=True, methods=['get'])
    def get_employee_by_room_in_enterpise(self,request,*args,**kwargs):
        try:
            idRoom = self.kwargs.get("room_id")
            employeeRooms = EmployeeRoom.objects.filter(room=idRoom)

            return Response({"employeesrooms": EmployeeRoomSerializer(employeeRooms,many=True).data, "msg": "success"}, status=status.HTTP_200_OK)

        except EmployeeRoom.DoesNotExist:
            return Response({"error": "La salle spécifiée n'existe pas."}, status=status.HTTP_404_NOT_FOUND)

        except Employee.DoesNotExist:
            return Response({"error": "L'employé associé à la salle n'existe pas."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                


########################################## Face viewset #######################################
class FacesViewSet(viewsets.ModelViewSet):
    serializer_class = FacesSerializer
    permission_classes = [IsAuthenticated]
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
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
            employee = self.kwargs.get("employee")
            instance = Face.objects.get(id=picture_id)
            serializer = self.serializer_class(instance=instance, data=request.data)
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
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    queryset = Room.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"msg":"success","room":serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


#####################################  EmployeeRoom ###########################################
class EmployeeRoomViewset(viewsets.ModelViewSet):
    serializer_class = EmployeeRoomSerializer
    permission_classes = [IsAuthenticated]
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    queryset = EmployeeRoom.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"msg":"success"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": f"{serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)



######################################## Qr visewset ##########################################
class QrViewset(viewsets.ModelViewSet):
    serializer_class = QrSerializer
    permission_classes = [IsAuthenticated]
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    queryset = Qr.objects.all()

    def create(self, request, *args, **kwargs):
        user = request.user
        employee_id = request.data.get("employee")
        
        try:
            qr_content = request.data.get("qr_code", "")
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")

            buffer = BytesIO()
            img.save(buffer, format="PNG")

            # Obtenir l'instance de l'employé à partir de l'ID
            employee_instance = get_object_or_404(Employee, id=employee_id)
            
            # Mettre à jour les Qr existants si is_current est vrai
            if request.data.get("is_current", False):
                Qr.objects.filter(employee=employee_instance).update(is_current=False)
            
            qr_instance = Qr.objects.create(
                qr_code=qr_content,
                employee=employee_instance,
                is_current=bool(request.data.get("is_current"))
            )
            qr_instance.qr_image.save(f"qrcode_{qr_instance.id}.png", ContentFile(buffer.getvalue()))

            # Ajouter l'URL vers l'image du code QR dans la réponse
            qr_instance_data = QrSerializer(qr_instance).data
            qr_instance_data["qr_image_url"] = request.build_absolute_uri(qr_instance.qr_image.url)

            return Response({"code_qr":qr_instance_data,"msg": "success"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
        

######################################SecurityCode Viewset ####################################
class SecurityCodeViewset(viewsets.ModelViewSet):
    serializer_class = SecurityCodeSerializer
    permission_classes = [IsAuthenticated]
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    queryset = SecurityCode.objects.all()

    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            serializer = self.get_serializer(data=request.data)
            print("Hello, we are here")
            
            if serializer.is_valid():
                # Get the employee for whom the code is being created
                employee = serializer.validated_data['employee']

                # Check if is_current is True
                if serializer.validated_data['is_current']:
                    # If is_current is True, set is_current to False for all other security codes of the employee
                    SecurityCode.objects.filter(employee=employee).update(is_current=False)

                # Save the new security code
                serializer.save()

                return Response({"code": serializer.data, "msg": "success"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": f"{serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST) 
        
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


class EconomicSectorViewSet(viewsets.ModelViewSet):
    queryset = EconomicSector.objects.all()
    serializer_class = EconomicSectorSerializer
    permission_classes = [IsAuthenticated]
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
