from rest_framework import serializers
from .models import Lead, User
from django.core.validators import EmailValidator, RegexValidator

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'address',
            'status',
            'company',
            'staff',
        )


    email = serializers.EmailField(validators=[
        EmailValidator(message="Invalid email address format"),
        RegexValidator(r'^[a-z0-9]+[\.a-z0-9_]*@[a-z0-9]+\.[a-z]{2,4}$',
                       message="Invalid email address format"),
    ])

    def create(self, validated_data):
        return Lead.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance