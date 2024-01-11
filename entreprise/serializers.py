from .models import AccesModel, Country, EconomicSector, EnterpriseAdmin, Enterprise, Employee, Face, Room, EmployeeRoom, Qr, SecurityCode, \
    EnterpriseAdminRole
from rest_framework import serializers
from django.db import models

from account.models import Custom_User

from swan_project.src.face_detection import convert_image_to_numpy_array, detect_face

from swan_project.src.verify_face import verify_face

from swan_project.src.code_qr import read_qr_code

from admins.models import SystemAdmin


################################ Enterprise Admin Seriallyser ###############################################

class EntrepriseAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnterpriseAdmin
        fields = '__all__'
        
    def validate(self,data):
        user = self.context['request'].user

        try:
            system_admin = SystemAdmin.objects.get(user_admin=user)
            return data
        except SystemAdmin.DoesNotExist:
            try:
                entreprise_creatrice = Enterprise.objects.get(creator=user)
                return data
            except Enterprise.DoesNotExist:
                raise  serializers.ValidationError("You have not permission to do this action")



################################## Enterprise Serializers #####################################################
class EnterpriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = '__all__' 
        
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     request = self.context.get('request')

    #     # Ajouter les URLs des fichiers aux données sérialisées
    #     data['director_card_file_url'] = request.build_absolute_uri(instance.director_card_file.url)
    #     data['rccm_file_url'] = request.build_absolute_uri(instance.rccm_file.url)
    #     data['logo_url'] = request.build_absolute_uri(instance.logo.url)

    #     return data

################################################# Complete enterprise information Serializer ################################################### 
class CompletEnterpiseInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = ['email', 'director_card_id', 'director_card_type', 'director_firstname','director_lastname', 'phone','description', 'adress', 'country','sectors','ifu','rcm']  
        
        def update(self, instance, validated_data):
            instance.director_firstname = validated_data.get('director_firstname', instance.director_firstname)
            instance.director_lastname = validated_data.get('director_lastname', instance.director_lastname)
            instance.director_card_id = validated_data.get('director_card_id', instance.director_card_id)
            instance.director_card_type = validated_data.get('director_card_type', instance.director_card_type)
            instance.phone = validated_data.get('phone', instance.phone)
            instance.description = validated_data.get('description', instance.description)
            instance.adress = validated_data.get('adress', instance.adress)
            instance.country = validated_data.get('country', instance.country)
            instance.sectors.set(validated_data.get('sectors', instance.sectors.all()))
            instance.ifu = validated_data.get('ifu', instance.ifu)
            instance.rcm = validated_data.get('rcm', instance.rcm)
            instance.email = validated_data.get('email', instance.email)
            instance.save()
            return instance 
        
#################################################### Add Enterprise Docs Serilizer############################################  
class AddEnterpriseDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = ['director_card_file', 'rccm_file','logo']
        
        
        
class EnterpriseRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = ['name', 'creator'] 
        

##################################Enterprise create Serializer #####################################################
class EnterpriseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = ['name', 'description', 'country', 'logo']

    def validate(self, data):
        user = self.context['request'].user
        request_method = self.context['request'].method
        if request_method == "put" or request_method == "patch" or request_method == "delete" \
                or request_method == 'post':
            try:
                system_admin = SystemAdmin.objects.get(user_admin=user)
                return data
            except SystemAdmin.DoesNotExist:
                try:
                    entreprise_creatrice = Enterprise.objects.get(creator=user)
                    return data
                except Enterprise.DoesNotExist:
                    try:
                        entreprise_admin = EnterpriseAdmin.objects.get(user=user)
                    except EnterpriseAdmin.DoesNotExist:
                        raise serializers.ValidationError("You have not permission to this action")
        else:
            return data



class EnterpriseCreateSerializerWithoutRegister(serializers.ModelSerializer):
    name = models.CharField(max_length=255)

    class Meta:
        model = Custom_User
        fields = ['firstname', 'lastname', 'email', 'name', 'password']


class EnterpriseValidationSerializer(serializers.ModelSerializer):
    director_card_file = serializers.CharField(source='picture.url', read_only=True)

    class Meta:
        model = Enterprise
        fields = ['ifu', 'rcm', 'director_card_id', 'director_card_file', 'director_card_type', 'director_lastname',
                  'director_firstname', 'director_card_file']


class EnterpriseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = '__all__'


########################################## Country serializers ####################################################
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


################################# Employee serializer #####################################################
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class CreateEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Custom_User
        fields = ["lastname", "firstname", 'email', "telephone", "password"]
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        user = self.context['request'].user

        # Vérifier si l'utilisateur est un "system_admin" en fonction de la relation SystemAdmin
        try:
            system_admin = SystemAdmin.objects.get(user_admin=user)
            return data
        except SystemAdmin.DoesNotExist:
            try:
                entreprise_creatrice = Enterprise.objects.filter(creator=user)
                return data
            except Enterprise.DoesNotExist:
                try:
                    entreprise_admin = EnterpriseAdmin.objects.get(user=user)
                except EnterpriseAdmin.DoesNotExist:
                    raise serializers.ValidationError("L'utilisateur n'a pas les permissions nécessaires.")

                request_method = self.context['request'].method

                if request_method == 'POST':
                    # Vérifier si l'utilisateur a le rôle "EnterpriseAdminRole"
                    try:
                        enterprise_admin_role = EnterpriseAdminRole.objects.get(entreprise_admin=entreprise_admin,
                                                                                role='add_employee')
                    except EnterpriseAdminRole.DoesNotExist:
                        raise serializers.ValidationError("L'utilisateur n'a pas le rôle requis.")

            return data


class UpdateEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Custom_User
        fields = ["lastname", "firstname", 'email', "telephone"]
        extra_kwargs = {'password': {'write_only': True}}


class FacesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Face
        fields = '__all__'

    def validate(self, data):
        image = convert_image_to_numpy_array(data.get("face_file"))
        detect_face_result = detect_face(image)
        if detect_face_result is None:
            raise serializers.ValidationError("No face detect in image or We dectect more than 2 face in images. Please change the image")

        else:
            print("One personne")
            face_verification = verify_face(employee=data.get('employee'), image=detect_face_result)
            if face_verification > 0.50:
                return data
            else:
                raise serializers.ValidationError("The probality of ressemblance between the images is less than 60%")

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

    def validate(self, data):
        user = self.context['request'].user
        request_method = self.context['request'].method
        if request_method == "put" or request_method == "patch" or request_method == "delete" or request_method == "post":
            try:
                system_admin = SystemAdmin.objects.get(user_admin=user)
                return data
            except SystemAdmin.DoesNotExist:
                try:
                    entreprise_creatrice = Enterprise.objects.get(creator=user)
                    return data
                except Enterprise.DoesNotExist:
                    try:
                            entreprise_admin = EnterpriseAdmin.objects.get(user=user)
                            try:
                                enterprise_admin_role = EnterpriseAdminRole.objects.get(entreprise_admin=entreprise_admin,
                                                                                        role='manage enterprise rooms')
                                return data
                            except EnterpriseAdminRole.DoesNotExist:
                                raise serializers.ValidationError("Yu have not permission to do this task")
                    except EnterpriseAdmin.DoesNotExist:
                        raise serializers.ValidationError("You have not permission to this action")
        else:
            return data


class EmployeeRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRoom
        fields = '__all__'
    def validate(self, data):
        user = self.context['request'].user
        try:
            system_admin = SystemAdmin.objects.get(user_admin=user)
            return data
        except SystemAdmin.DoesNotExist:
            try:
                entreprise_creatrice = Enterprise.objects.filter(creator=user)
                return data
            except Enterprise.DoesNotExist:
                try:
                        entreprise_admin = EnterpriseAdmin.objects.get(user=user)
                        try:
                            enterprise_admin_role = EnterpriseAdminRole.objects.get(entreprise_admin=entreprise_admin,
                                                                                    role='manage employee_room')
                            return data
                        except EnterpriseAdminRole.DoesNotExist:
                            raise serializers.ValidationError("Yu have not permission to do this task")
                except EnterpriseAdmin.DoesNotExist:
                    raise serializers.ValidationError("You have not permission to this action")
class QrSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qr
        fields = ["is_current","qr_code","employee"] 
        
    def validate(self,data): 
        user = self.context['request'].user
        request_method = self.context['request'].method
        if request_method == "put" or request_method == "patch" or request_method == "delete" or \
                request_method == "post":
            try:
                system_admin = SystemAdmin.objects.get(user_admin=user)
                qr_content = read_qr_code(image_path=data.get("qr_image"))
                print(qr_content)
                if qr_content == data.get("qr_code"):
                    return data
                else:
                    raise serializers.ValidationError("Qr content not conform to qr code")
            except SystemAdmin.DoesNotExist:
                try:
                    entreprise_creatrice = Enterprise.objects.get(creator=user)
                    qr_content = read_qr_code(image_path=data.get("qr_image"))
                    print(qr_content)
                    if qr_content == data.get("qr_code"):
                        return data
                    else:
                        raise serializers.ValidationError("Qr content not conform to qr code")
                except Enterprise.DoesNotExist:
                    try:
                        entreprise_admin = EnterpriseAdmin.objects.get(user=user)
                        try:
                            enterprise_admin_role = EnterpriseAdminRole.objects.get(
                                entreprise_admin=entreprise_admin,
                                role='manage employee qr_code')
                            qr_content = read_qr_code(image_path=data.get("qr_image"))
                            print(qr_content)
                            if qr_content == data.get("qr_code"):
                                return data
                            else:
                                raise serializers.ValidationError("Qr content not conform to qr code")
                        except EnterpriseAdminRole.DoesNotExist:
                            raise serializers.ValidationError("Yu have not permission to do this task")
                    except EnterpriseAdmin.DoesNotExist:
                        raise serializers.ValidationError("You have not permission to this action")
        else:
            try:
                system_admin = SystemAdmin.objects.get(user_admin=user)
                qr_content = read_qr_code(image_path=data.get("qr_image"))
                print(qr_content)
                if qr_content == data.get("qr_code"):
                    return data
                else:
                    raise serializers.ValidationError("Qr content not conform to qr code")
            except SystemAdmin.DoesNotExist:
                try:
                    entreprise_creatrice = Enterprise.objects.get(creator=user)
                    qr_content = read_qr_code(image_path=data.get("qr_image"))
                    print(qr_content)
                    if qr_content == data.get("qr_code"):
                        return data
                    else:
                        raise serializers.ValidationError("Qr content not conform to qr code")
                except Enterprise.DoesNotExist:
                    try:
                        entreprise_admin = EnterpriseAdmin.objects.get(user=user)
                        try:
                            enterprise_admin_role = EnterpriseAdminRole.objects.get(
                                entreprise_admin=entreprise_admin,
                                role='manage employee security code')
                            return data
                        except EnterpriseAdminRole.DoesNotExist:
                            raise serializers.ValidationError("You have not permission to do this task")
                    except EnterpriseAdmin.DoesNotExist:
                        try:
                            employee = SecurityCode.objects.get(employee=user)
                            qr_content = read_qr_code(image_path=data.get("qr_image"))
                            print(qr_content)
                            if qr_content == data.get("qr_code"):
                                return data
                            else:
                                raise serializers.ValidationError("Qr content not conform to qr code")
                        except SecurityCode.DoesNotExist:
                            raise serializers.ValidationError("Yu have not permission to do this task")


################################ Security code Serializer ##########################################"""
class SecurityCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityCode
        fields = '__all__'

    def validate(self, data):
        user = self.context['request'].user
        request_method = self.context['request'].method
        if request_method == "put" or request_method == "patch" or request_method == "delete" or request_method == "post":
            try:
                system_admin = SystemAdmin.objects.filter(user_admin=user)
                return data
            except SystemAdmin.DoesNotExist:
                try:
                    entreprise_creatrice = Enterprise.objects.filter(creator=user)
                    return data
                except Enterprise.DoesNotExist:
                    try:
                        entreprise_admin = EnterpriseAdmin.objects.get(user=user)
                        try:
                            enterprise_admin_role = EnterpriseAdminRole.objects.get(entreprise_admin=entreprise_admin,
                                                                                    role='manage employee security code')
                            return data
                        except EnterpriseAdminRole.DoesNotExist:
                            raise serializers.ValidationError("Yu have not permission to do this task")
                    except EnterpriseAdmin.DoesNotExist:
                        raise serializers.ValidationError("You have not permission to this action")
        else:
            try:
                system_admin = SystemAdmin.objects.get(user_admin=user)
                return data
            except SystemAdmin.DoesNotExist:
                try:
                    entreprise_creatrice = Enterprise.objects.filter(creator=user)
                    return data
                except Enterprise.DoesNotExist:
                    try:
                        entreprise_admin = EnterpriseAdmin.objects.get(user=user)
                        try:
                            enterprise_admin_role = EnterpriseAdminRole.objects.get(entreprise_admin=entreprise_admin,
                                                                                    role='manage employee security code')
                            return data
                        except EnterpriseAdminRole.DoesNotExist:
                            raise serializers.ValidationError("You have not permission to do this task")
                    except EnterpriseAdmin.DoesNotExist:
                        try:
                            employee = SecurityCode.objects.get(employee=user)
                            return data
                        except SecurityCode.DoesNotExist:
                            raise serializers.ValidationError("Yu have not permission to do this task")


#########################################  Rôle Serializer #####################################
class EnterpriseAdminRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnterpriseAdminRole
        fields = '__all__'

    def validate(self, data):
        user = self.context['request'].user
        request_method = self.context['request'].method
        if request_method == "put" or request_method == "patch" or request_method == "delete" or request_method == "post":
            try:
                system_admin = SystemAdmin.objects.get(user_admin=user)
                return data
            except SystemAdmin.DoesNotExist:
                try:
                    entreprise_creatrice = Enterprise.objects.get(creator=user)
                    return data
                except Enterprise.DoesNotExist:
                    try:
                        entreprise_admin = EnterpriseAdmin.objects.get(user=user)
                        try:
                            enterprise_admin_role = EnterpriseAdminRole.objects.get(entreprise_admin=entreprise_admin,
                                                                                    role='add_interprise_admin')
                            return data
                        except EnterpriseAdminRole.DoesNotExist:
                            raise serializers.ValidationError("Yu have not permission to do this task")
                    except EnterpriseAdmin.DoesNotExist:
                        raise serializers.ValidationError("You have not permission to this action")
        else:
            return data

class EconomicSectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EconomicSector
        fields = '__all__' 
        
        
##############################################################  Access Model Serializer ###########################################################


class AccesModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccesModel
        fields = '__all__'
