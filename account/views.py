from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from rest_framework import generics, status, parsers
from rest_framework.decorators import authentication_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone

from entreprise.serializers import EnterpriseSerializer, EnterpriseRegisterSerializer
from .models import Custom_User,ActivationCode
from .serializers import CompleteUserInformationSerializer, UserLoginSerializer, UserRegistrationSerializer, SendPasswordResetEmailSerializer, \
    UserChangePasswordSerializer, UserPasswordResetSerializer, UserProfileSerializer, UpdateProfilePictureSerializer, \
    UpdateUserSerializer, ChangeEmailSerializer,SendActivationCodeSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    """
    This function use to get token for User when he is registering
    :param user: (user: Any)
    :return:  dict[str, str]
    """
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


############################################################# Create user with enterpise  ############################################################
class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

    def post(self, request, *args, **kwargs):
        """
        We redefine the post function for UserRegistrationView.It's being used to  save a new user register
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            enterprise_name = request.data.get("enterprise_name")
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()

                #Let's create enterprise
                if user and user.id:
                    enterprise_name = serializer.validated_data.get('enterprise_name', '')
                    enterprise_data = {
                        'creator': user.id,
                        'name': enterprise_name,
                    }
                enterprise_serializer = EnterpriseRegisterSerializer(data=enterprise_data)
                if enterprise_serializer.is_valid():
                    enterprise_serializer.save()
                    return Response({"msg": "Registration successful. Active now your account"}, status=status.HTTP_201_CREATED)
                else:
                    user.delete()
                    return Response(enterprise_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


##################################################################  Send Activation code Views #######################################################
class SendActivationCodeView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SendActivationCodeSerializer
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

    @swagger_auto_schema(
        operation_description="Endpoint Login",
        request_body = SendActivationCodeSerializer
    ) 

    def post(self, request, *args, **kwargs):
        serializer = SendActivationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "Activation code sent successfully."}, status=status.HTTP_200_OK)


############################################################## Verify activation code ################################################################# 
class VerifyActivationCodeView(APIView):

    def post(self, request, activation_code,*args, **kwargs):
       
        if not activation_code:
            return Response({"error": "Activation code is required."}, status=status.HTTP_400_BAD_REQUEST)

        # search activation code in temporary table
        activation_code_obj = ActivationCode.objects.filter(code=activation_code).first()
        if activation_code_obj:
            if not activation_code_obj.is_expired():
                # upadate is_activate fields for user 
                user = activation_code_obj.user
                user.is_validate = True
                user.save()
            # delete code from temporary table
            activation_code_obj.delete()

            return Response({"message": "Activation successful."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid or expired activation code."}, status=status.HTTP_400_BAD_REQUEST)



################################################# Login Sérializer #######################################################################################
@authentication_classes([])
class UserLoginView(APIView):
    permission_classes = [AllowAny]
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    serializer_class = UserLoginSerializer

    @swagger_auto_schema(
        operation_description="Endpoint Login",
        request_body=UserLoginSerializer
    )
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = Custom_User.objects.get(email=email)
        print(user)
        # user = authenticate(email=email, password=password)

        if user is not None:
            if check_password(password, user.password):
                token = get_tokens_for_user(user)
                print(user.password)
                user_data = {
                    'id': user.id,
                    'email': user.email,
                    'lastname': user.lastname,
                    'name': user.name,
                    'firstname': user.firstname,
                    'username': user.username,
                    'sexe': user.sexe,
                    'telephone': user.telephone,
                    'picture': str(user.picture),
                    'birth_date': user.birth_date,
                    'adresse': user.adresse,
                    'description': user.description,
                    'profession': user.profession,
                }
                return Response({'token': token, 'user': user_data, 'msg': 'Login Sucess'}, status=status.HTTP_200_OK)

        return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}},
                        status=status.HTTP_404_NOT_FOUND)


# Send mail to get password
class SendPasswordResetEmailView(APIView):
    serializer_class = SendPasswordResetEmailSerializer
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

    @swagger_auto_schema(
        operation_description="Endpoint Login",
        request_body=SendPasswordResetEmailSerializer

    )
    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': "Password Reset Sucessfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

############################################### Complete User Information view ##################################################### 
class CompleteUserInformationView(APIView):
    serializer_class = CompleteUserInformationSerializer
    permission_classes = [IsAuthenticated]
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    
    @swagger_auto_schema(
        operation_description="Complete User information",
        request_body=CompleteUserInformationSerializer
    ) 
    
    def post(self, request, *args, **kwargs):
        serializer = CompleteUserInformationSerializer(data = request.data)
        if serializer.is_valid():
            user_instance = request.user  
            serializer.update(user_instance, serializer.validated_data)
            updated_user = Custom_User.objects.get(id = user_instance.id) 
            user_data = {
                    'id':updated_user.id,
                    'email':updated_user.email,
                    'lastname':updated_user.lastname,
                    'name':updated_user.name,
                    'firstname':updated_user.firstname,
                    'username':updated_user.username,
                    'sexe':updated_user.sexe,
                    'telephone':updated_user.telephone,
                    'picture': str(updated_user.picture),
                    'birth_date':updated_user.birth_date,
                    'adresse':updated_user.adresse,
                    'description':updated_user.description,
                    'profession':updated_user.profession,
                }
            return Response({"message": "User information updated successfully", "user": user_data}, status=status.HTTP_200_OK)        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


####################################### Complete user informations by userId ########################################### 

class CompleteUserInforByUserIdView(APIView):
    serializer_class = CompleteUserInformationSerializer
    permission_classes = [IsAuthenticated]
    #parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser) 
    
    @swagger_auto_schema(
        operation_description="Endpoint Login",
        request_body= CompleteUserInformationSerializer

    )
    def post(self,  request, *args, **kwargs):
        try:
            print("hahah"*100)
            userId = kwargs.get("userId")
            user = Custom_User.objects.get(id=userId)

            # Use the serializer to update user information
            serializer = CompleteUserInformationSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"msg": "User information updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Custom_User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# Change password whan user is authenticated
class UserChangePasswordView(APIView):
    serializer_class = UserChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

    @swagger_auto_schema(
        operation_description="Endpoint Login",
        request_body=UserChangePasswordSerializer

    )
    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': "Password changed"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Change password when user forget it
class UserPasswordResetView(APIView):
    serializer_class = UserPasswordResetSerializer
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

    @swagger_auto_schema(
        operation_description="Changement de password",
        request_body=UserPasswordResetSerializer
    )
    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, "token": token})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': "Password Reset Sucessfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View to get user Informations
class UserProfileView(APIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Update profilPicture views
class UpdateProfilePictureView(APIView):
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

    @swagger_auto_schema(
        operation_description="Update Profile",
        request_body=UpdateProfilePictureSerializer

    )
    def post(self, request):
        user = request.user
        serializer = UpdateProfilePictureSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "Profile picture updated"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Update profil  user profil view
class UpdateUserView(APIView):
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    @swagger_auto_schema(
        operation_description="Mise a jour profile",

        request_body=UpdateUserSerializer,

    )
    def post(self, request):
        user = request.user
        if user is None:
            return Response({"error": "Assurez voud d'etre connecté"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UpdateUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

    @swagger_auto_schema(
        operation_description="Change email",

        request_body=ChangeEmailSerializer,

    )
    def put(self, request):
        serializer = ChangeEmailSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)
            return Response({'message': 'Adresse e-mail mise à jour avec succès.'})
        return Response(serializer.errors, status=400)

from django.shortcuts import render

# Create your views here.
