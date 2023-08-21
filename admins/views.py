from django.contrib.auth.hashers import check_password
from django.shortcuts import render, get_object_or_404

from rest_framework import viewsets, status, parsers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from account.models import Custom_User
from account.serializers import UserSerializer, UserLoginSerializer
from account.views import get_tokens_for_user
from admins.serializer import SystemAdminsSerialyser, ManageEnterpriseSerializer
from entreprise.models import Enterprise
from rest_framework.views import APIView

from admins.models import SystemAdmin

from account.serializers import SendPasswordResetEmailSerializer, UserPasswordResetSerializer, UserChangePasswordSerializer, UserProfileSerializer

from account.utils import Util

from entreprise.serializers import EnterpriseSerializer


# Create your views here.


class SystemAdminLogin(APIView):

    serializer_class = UserLoginSerializer
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

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

        if user is not None:
            if check_password(password, user.password):
                try:
                    admin = SystemAdmin.objects.get(user_admin=user)
                    print(admin)
                    token = get_tokens_for_user(user)
                    print(user.password)
                    return Response({'token': token, 'msg': 'Login Sucess'}, status=status.HTTP_200_OK)
                except Exception as e:
                    print(e)
                    return Response({'errors': "You are not in admin list"}, status=status.HTTP_404_NOT_FOUND)

        return Response({'errors': {'non_field_errors': ['Email or Password is not Valid']}},
                        status=status.HTTP_404_NOT_FOUND)


##### Forget Password
class SystemAdminSendPasswordResetEmailView(APIView):
    serializer_class = SendPasswordResetEmailSerializer
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

    @swagger_auto_schema(
        operation_description="Endpoint Login",
        request_body=SendPasswordResetEmailSerializer

    )
    def post(self, request, format=None):
        email = request.data.get('email')
        user = Custom_User.objects.get(email=email)
        if user is not None:
            admin = SystemAdmin.objects.get(user_admin=user)
            if admin is not None:
                serializer = SendPasswordResetEmailSerializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    return Response({'msg': f"We send email to {email}"}, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'errors': "You are not in admin list"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "Any user use this email"}, status=status.HTTP_404_NOT_FOUND)




class AdminUserPasswordResetView(APIView):
    serializer_class = UserPasswordResetSerializer
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)

    @swagger_auto_schema(
        operation_description="Changement de password",
        request_body=UserPasswordResetSerializer
    )
    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, "token": token})
        user = request.user
        if serializer.is_valid(raise_exception=True):
            admin = SystemAdmin.objects.get(user_admin=user)
            print(admin)
            if admin is not None:
                return Response({'msg': "Password Reset Sucessfully"}, status=status.HTTP_200_OK)
            else:
                return Response({'errors': "You are not in admin list"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminUserChangePasswordView(APIView):
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


class AdminUserProfileView(APIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        adminaccount = SystemAdmin.objects.get(user_admin=request.user)
        if adminaccount is not None:
            print(adminaccount)
            return Response({"User": serializer.data, "Admin": f"{adminaccount.id}" }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ManageEnterpriseViews(viewsets.ModelViewSet):
    serializer_class = ManageEnterpriseSerializer
    #permission_classes = [IsAuthenticated]
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    queryset = Enterprise.objects.all()
    body = {}
    subject = "Reponse à votre demande de Validation"

    def list(self, request):
        try:
            queryset = Enterprise.objects.all()
            serializer = self.serializer_class(queryset, many=True)
            print(serializer.data)
            return Response(serializer.data)
        except Exception as e:
            return Response({"Error": f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def retrieve(self, request, pk=None):
        queryset = Enterprise.objects.all()
        enterprise = get_object_or_404(queryset, pk=pk)
        serializer =self.serializer_class(enterprise)
        return Response(serializer.data)



    def update(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance, data=request.data, partial=True)
        try:
            if serializer.is_valid():
                enterprise = get_object_or_404(Enterprise, id=pk)
                #print(enterprise.creator)
                if enterprise is not None:
                    user = Custom_User.objects.filter(id=enterprise.creator_id)
                    print(f"Interprise status {enterprise.status}")
                    print(f"Serializer status {request.data.get('status')}")
                    if enterprise.status != request.data.get("status"):
                        if request.data.get("status") == 1:
                            # let's send the mail to user
                            self.body = "Les informations que vous aviez fournie pour votre entreprise ont été analysées et approuvées avec succès"

                        elif request.data.get("status") == 0:
                            self.body ={"Votre entreprise est passé en mode non validé.Veuillez fournir les dossiers nécéssaires pour la validation de ce dernier"}

                        else:
                            self.body = {"La requête de validation n'a pas été approuvées. les informations fournie fournie ne sont pas valides"}

                    else:
                        self.body = {"Des modifications ont été effectuées sur votre entreprise."}

                    serializer.save()

                    data = {
                        'subject': f"{self.subject}",
                        "body": f"{self.body}",
                        "to_email": f"{user[0].email}"
                    }
                    Util.send_mail(data)
                    return Response(data=serializer.data, status=status.HTTP_201_CREATED)

            else:
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error":f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def destroy(self, request, pk=None):
        instance = self.get_object()

        instance.delete()
        return Response({"message": "Delete succes"}, status=status.HTTP_204_NO_CONTENT)


    @action(detail=False, methods=['get'], url_name="enterprise_refused")
    def by_status0(self, request):
        queryset = Enterprise.objects.filter(status=0)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


    @action(detail=False, methods=['get'], url_name="enterprise_accepted")
    def by_status_valid(self, request):
        queryset = Enterprise.objects.filter(status=1)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)



    @action(detail=False, methods=['get'], url_name="enterprise_")
    def by_status_refuse(self, request):
        queryset = Enterprise.objects.filter(status=-1)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

