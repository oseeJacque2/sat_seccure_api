
from .models import Country, EnterpriseAdmin, Enterprise
from rest_framework import serializers
from django.db import models

from account.models import User


################################ Enterprise Admin Seriallyser ###############################################

class EntrepriseAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnterpriseAdmin
        fields = '__all__'



##################################Enterprise Serializers #####################################################

class EnterpriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = '__all__'
        """
    def create(self, validated_data):
        admin_data = {'user': self.context['request'].user, 'is_creator': True}
        enterprise = Enterprise.objects.create(**validated_data)
        admin = EnterpriseAdmin.objects.create(**admin_data)
        admin.enterprises.set([enterprise])
        return enterprise """

class EnterpriseCreateSerializerWithoutRegister(serializers.ModelSerializer):

    name = models.CharField(max_length=255)
    class Meta:
        model = User
        fields = ['firstname', 'lastname', 'email', 'name', 'password']



class EnterpriseLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']


class EnterpriseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = '__all__'



########################################## Country serializers ####################################################
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'