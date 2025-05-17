from rest_framework import serializers

from user.models import User
from user.serializer import *

from .models import *


class SchoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = School
        fields = ["id", "name", "manager"]

    def validate_manager(self, value):
        if value.user_type != "manager":
            raise ValidationError("The assigned user is not a manager.")
        return value


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "name"]


class ClassSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    students = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Class
        fields = ["id", "name", "teacher", "school", "students", "lessons"]


class StudentClassSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Class
        fields = ["id", "name", "teacher", "school", "lessons"]


class CreateClassSerializer(serializers.ModelSerializer):

    class Meta:
        model = Class
        fields = ["name", "school", "teacher"]

    def validate(self, data):
        teacher = data.get("teacher")
        if teacher.user_type != "teacher":
            raise ValidationError("The assigned user is not a teacher.")
        return data


class AddRemoveStudentClassSerializer(serializers.ModelSerializer):
    national_id = serializers.CharField(max_length=10)

    def validate_national_id(self, value):
        if len(value) != 10:
            raise ValidationError("National id must be 10 digits")
        if not value.isdigit():
            raise ValidationError("National id must contain only numbers")
        try:
            student = User.objects.get(natinal_id=value, user_type="student")
        except User.DoesNotExist:
            raise ValidationError(f"No student was found with {value} natinal id")
        return value

    class Meta:
        model = Class
        fields = ["id", "name", "teacher", "school", "students", "lessons"]
        read_only_fields = ["id", "name", "teacher", "school", "lessons"]
