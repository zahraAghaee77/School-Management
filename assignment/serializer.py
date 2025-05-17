import os

from django.core.exceptions import *
from django.utils import timezone
from rest_framework import serializers

from school.models import *
from school.serializer import *

from .models import *


def validate_attachment(value):
    extension = os.path.splitext(value.name)[1]
    if not extension.lower() in [".pdf", ".zip"]:
        raise ValidationError("You should upload PDF or ZIP file.")
    return value


def validate_answer_file(value):
    extension = os.path.splitext(value.name)[1]
    if not extension.lower() in [".pdf", ".zip"]:
        raise ValidationError("You should upload PDF or ZIP file.")
    return value


class AssignmentSerializer(serializers.ModelSerializer):
    class_obj = ClassSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)
    attachment = serializers.FileField(
        allow_empty_file=False, validators=[validate_attachment], required=False
    )

    def validate(self, data):
        if data["class_obj"].user != self.context["request"].user:
            raise ValidationError(
                "You do not have access to create assignments for this class."
            )
        if data["lesson"] not in data["class_obj"].lessons.all():
            raise ValidationError("This lesson does not belong to this class.")
        if data["grade"] > 100:
            raise ValidationError("The grade must not be greater than 100.")
        if data["deadline"] <= self.instance.created_at:
            raise ValidationError("The deadline must be later than creation time.")
        if data["answer_text"] is None and data["answer_file"] is None:
            raise ValidationError("You must type answer or upload answer's file.")
        return data

    class Meta:
        model = Assignment
        fields = [
            "id",
            "title",
            "context",
            "deadline",
            "attachment",
            "last_modified",
            "class_obj",
            "lesson",
        ]
        read_only_fields = ["last_modified", "created_at"]


class CreateAssignmentSerializer(serializers.ModelSerializer):
    class_obj = ClassSerializer()
    lesson = LessonSerializer()
    attachment = serializers.FileField(
        allow_empty_file=False, required=False, validators=[validate_attachment]
    )

    def validate(self, data):
        if data["class_obj"].user != self.context["request"].user:
            raise ValidationError(
                "You do not have access to create assignments for this class."
            )
        if data["lesson"] not in data["class_obj"].lessons.all():
            raise ValidationError("This lesson does not belong to this class.")
        if data["grade"] > 100:
            raise ValidationError("The grade must not be greater than 100.")
        if data["deadline"] <= self.instance.created_at:
            raise ValidationError("The deadline must be later than creation time.")
        return data

    class Meta:
        model = Assignment
        fields = [
            "title",
            "context",
            "deadline",
            "attachment",
            "last_modified",
            "class_obj",
            "lesson",
        ]
        read_only_fields = ["last_modified", "created_at"]


"""  
class AssignmentSolutionSerializer(serializers.ModelSerializer):
    answer_file = serializers.FileField(
        validators=[validate_answer_file],
        allow_empty_file=False,
        required=False,
    )

    def validate(self, data):
        if data["answer_text"] is None and data["answer_file"] is None:
            raise ValidationError("You must type answer or upload answer's file.")
        return data

    class Meta:
        model = Assignment
        fields = ["answer_text", "answer_file"]
"""

"""  
class TeacherSolutionsSerializer(serializers.ModelSerializer):
    def validate_grade(self, value):
        if value > 100:
            raise ValidationError("The grade must not be greater than 100.")
        return value

    class Meta:
        modele = Solution
        fields = "__all__"
        read_only_fields = [
            "context",
            "created_at",
            "attachment",
            "last_modified",
            "student",
            "assignment",
        ]

"""


class SolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = "__all__"
        read_only_fields = ["created_at", "last_modified", "student", "grade"]

    def validate_grade(self, value):
        if value > 100:
            raise ValidationError("The grade must not be greater than 100.")
        return value

    def validate(self, data):
        assignment = data.get("assignment")
        if assignment.deadline < timezone.now():
            raise serializers.ValidationError("The assignment deadline has passed.")
        if data["context"] is None and data["attachment"] is None:
            raise ValidationError("You must type answer our upload answer's file.")
        return data


"""  
class StudentSolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = "__all__"
        read_only_fields = [
            "created_at",
            "last_modified",
            "student",
        ]

    def validate(self, data):
        user = self.context["request"].user
        assignment = data["assignment"]
        if not assignment.class_obj.students.filter(id=user.id).exists():
            raise ValidationError("You do not have access to this assignment.")
        return data


class StudentCreateSolutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = [
            "context",
            "attachment",
            "assignment",
        ]
        read_only_fields = [
            "created_at",
            "last_modified",
            "student",
        ]

    def validate(self, data):
        user = self.context["request"].user
        assignment = data["assignment"]
        if not assignment.class_obj.students.filter(id=user.id).exists():
            raise ValidationError("You do not have access to this assignment.")
        if data["context"] is None and data["attachment"] is None:
            raise ValidationError("You must type answer our upload answer's file.")
        if assignment.deadline < timezone.now():
            raise ValidationError("The deadline was arrived.")
        return data
"""
