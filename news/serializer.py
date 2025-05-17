from rest_framework import serializers

from school.serializer import *
from user.serializer import *

from .models import *


class NewsSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    school = SchoolSerializer(read_only=True)
    class_obj = ClassSerializer(read_only=True)

    class Meta:
        model = News
        fields = [
            "id",
            "title",
            "context",
            "created_at",
            "last_modified",
            "creator",
            "school",
            "class_obj",
        ]

    def validate(self, data):
        if self.context["request"].user.user_type == "student":
            student = self.context["request"].user
            student_classes = Class.objects.filter(students=student)
            student_schools = {
                class_student.school for class_student in student_classes
            }
            if self.class_obj not in student_classes or not (
                self.school in student_schools and self.creator.user_type == "manager"
            ):
                raise ValidationError("You do not have permission to access this news.")

        return data


class ManagerNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = [
            "title",
            "context",
            "created_at",
            "last_modified",
            "school",
        ]
        read_only_fields = [
            "creator",
        ]

    def validate(self, data):
        if not data.get("school"):
            raise ValidationError("You should specify your school.")
        return data


class TeacherNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = [
            "title",
            "context",
            "created_at",
            "last_modified",
            "class_obj",
        ]
        read_only_fields = [
            "creator",
        ]

    def validate(self, data):
        if not data.get("class_obj"):
            raise ValidationError("You should specify your class.")
        return data
