from .models import User,UserRequest,CompanyRequest
from rest_framework import serializers

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserRequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRequest
        fields = "__all__"


class CompanyRequestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyRequest
        fields = "__all__"