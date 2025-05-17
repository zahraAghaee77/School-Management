from django.contrib.auth.hashers import make_password
from django.core.exceptions import *
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "bio",
            "user_type",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "national_id",
            "username",
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "user_type",
        ]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise ValidationError("Password does not match.")
        if len(data["national_id"]) != 10 or not data["national_id"].isdigit():
            raise ValidationError("Your national id must be 10 digits.")
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User(**validated_data)
        user.is_active = False
        user.set_password(validated_data["password"])
        user.save()
        return user


class UpdateBioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("bio",)
