from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Custom_User,ActivationCode
from .utils import Util
from django.core.mail import send_mail

from admins.models import SystemAdmin


#######################################################User Serializer ##################################################################""
class UserSerializer(serializers.Serializer):
    class Meta:
        model = Custom_User
        fields = '__all__' 
        
        
#################################################### User  serializer registerSerializer ###################################################################
class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    This class Serilizer is define for user registration.We will use a class attribut password2 to verifie if the user is sure for his password
    """
    password2 = serializers.CharField(style={'input_type': "password"}, write_only=True)
    enterprise_name = serializers.CharField(max_length=255, default="")
    class Meta:
        model = Custom_User
        fields = ["email", "enterprise_name", "telephone", "password", "password2"]
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        """
        This function is use to validate user input password
        :param attrs:{get}
        :return: attrs
        """
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError('Password and Confirm Password doesn\'t match')
        return attrs

    def create(self, validated_data):
        """
        Used to create User in DB
        :param validated_data: {__contains__, __getitem__}
        :return:  User
        """
        password = validated_data.pop('password2')
        enterpise_name = validated_data.pop('enterprise_name')
        user = Custom_User.objects.create_user(**validated_data)
        return user


################################################# Send Activation code Sérializer ########################################################################""
class SendActivationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = Custom_User
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get('email')

        if Custom_User.objects.filter(email=email).exists():
            user = Custom_User.objects.get(email=email)

            # verify if we are  a valid activate code for user in the table 
            existing_code = ActivationCode.objects.filter(user=user).first()
            if existing_code and not existing_code.is_expired():
                raise serializers.ValidationError("Activation code still valid.")

            # Generate new code validation 
            activation_code = Util.generate_activation_code()

            # save the new code validation in the table
            ActivationCode.objects.update_or_create(user=user, defaults={'code': activation_code})

            # send email to user
            body = f"Your activation code is: {activation_code}"
            data = {
                'subject': "Activation Code",
                "body": body,
                "to_email": user.email
            }
            Util.send_mail(data)

            return attrs
        else:
            raise serializers.ValidationError("User not found.")



##################################################### Login Serializer ##########################################################################
class UserLoginSerializer(serializers.ModelSerializer):
    """
    Class for User Login.
    """
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = Custom_User
        fields = ["email", "password"]


############################################## Complete user Information serializer ##########################################

class CompleteUserInformationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Custom_User 
        fields = ["lastname", "firstname", "telephone", "sexe", "profession", "description", "birth_date","adresse"] 
        
    def update(self, instance, validated_data):
        # updated each valide fields
        for field, value in validated_data.items():
            setattr(instance, field, value)

        # Save the modification 
        instance.save()

        return instance

#####################################################################################################################################################################
class UserChangePasswordSerializer(serializers.Serializer):
    """
        Serializer class for user to allow to change the password when it authenticate
    """
    password = serializers.CharField(max_length=255, style={'input_type': "password"}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': "password"}, write_only=True)

    class Meta:
        fields = ['password', "password2"]

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get("password2")
        user = self.context.get('user')
        admin = SystemAdmin.objects.get(user_admin=user)
        print(admin)
        if admin is not None:
            if password != password2:
                raise serializers.ValidationError("Password and confirm Password doesn\'t match")
            user.set_password(password)
            user.save()
            return attrs
        else:
            raise serializers.ValidationError("You are not in admin list")





class SendPasswordResetEmailSerializer(serializers.Serializer):
    """
    Serilaizer class for user to ask process to change his password when he forget it
    We get it email and send him the token and Uid which help him to change his passord
    """
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = Custom_User
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')

        if Custom_User.objects.filter(email=email).exists:
            user = Custom_User.objects.get(email=email)
            #Encode the uid
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print(uid)
            #reset token for the user
            token = PasswordResetTokenGenerator().make_token(user)
            print(f"tokenn", token)

            #let's send the mail to user
            body = f"\n Uid: {uid} \n Token: {token}"
            data = {
                'subject': "Reset Yout Password ",
                "body": body,
                "to_email": user.email
            }
            Util.send_mail(data)
            #send_mail("Reset Yout Password", "Click this link to change your mail", "oseesoke@gmail.com", [f"{user.email}"])
            return attrs
        else:
            raise ValidationError("You are not a Registered User")



class UserPasswordResetSerializer(serializers.Serializer):

    """
        Serializer class to allow user change his password after get the resetpassword mail
    """
    password = serializers.CharField(max_length=255, style={'input_type': "password"}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type': "password"}, write_only=True)

    class Meta:
        fields = ['password', "password2"]

    def validate(self, attrs):
       try:
           password = attrs.get('password')
           password2 = attrs.get('password2')
           uid = self.context.get('uid')
           token = self.context.get('token')

           if password != password2:
               raise serializers.ValidationError('Password and Confirm Password doesn\'t match')
           id = smart_str(urlsafe_base64_decode(uid))
           user = Custom_User.objects.get(id=id)
           if not PasswordResetTokenGenerator().check_token(user, token):
               raise ValidationError('Token is not valid or expired')

           user.set_password(password)
           user.save()
           return attrs

       except DjangoUnicodeDecodeError as identifier:
           PasswordResetTokenGenerator().check_token(user,token)
           raise ValidationError('Token is not valid')



class UpdateUserSerializer(serializers.ModelSerializer):
    """
        Serializer for User to update his information
    """
    class Meta:
        model = Custom_User
        fields = ['email', "lastname", "firstname", "telephone", 'adresse']

class UpdateProfilePictureSerializer(serializers.ModelSerializer):
    """
        Serializer class to allow user to change profil picture
    """
    class Meta:
        model = Custom_User
        fields = ['picture', ]



class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer class for getting user information
    """
    picture_url = serializers.SerializerMethodField()

    class Meta:
        model = Custom_User
        fields = ['id', 'email', 'picture_url', 'firstname']

    def get_picture_url(self, obj):
        picture = getattr(obj, 'picture', None)
        if picture:
            return picture.url
        return None

class ChangeEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    password = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        fields = ["new_email", "password"]

    def validate_password(self, value):
        user = self.context["request"].user
        if not authenticate(username=user.email, password=value):
            raise serializers.ValidationError("Mot de passe incorrect")
        return value

    def update(self, instance, validated_data):
        instance.email = validated_data.get('new_email', instance.email)
        instance.save()
        return instance

