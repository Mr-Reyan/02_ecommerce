from .models import *
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import Tenant

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        tenant = Tenant.objects.get(id=2)

        return User.objects.create_user(
            **validated_data,
            tenant=tenant
        )


class LoginSerializer(TokenObtainPairSerializer):
    username_field = "username"