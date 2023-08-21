from rest_framework import serializers

from admins.models import SystemAdmin
from entreprise.models import Enterprise

from entreprise.models import EnterpriseAdmin


class SystemAdminsSerialyser(serializers.ModelSerializer):

    class Meta:
        model = SystemAdmin
        fields = ['user_admin']

class ManageEnterpriseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Enterprise
        fields = '__all__'

        """def validate(self, data):
            user = self.context["request"].user
            if not EnterpriseAdmin.objects.filter(user=user).exists():
                raise serializers.ValidationError("You are not admin User")

            return data """
