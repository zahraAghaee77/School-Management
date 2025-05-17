from rest_framework.permissions import BasePermission

from .models import *


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == "teacher"


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == "manager"


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == "student"


class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return request.user.is_staff or request.user.user_type == "manager"
        return True


class IsStudentReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return False
        return True


class IsMemberOfSchool(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, "school_manager"):
            return obj.school == request.user.school_manager

        if request.user.user_type == "teacher":
            return obj.school in [
                cls.school for cls in request.user.class_teacher.all()
            ]

        if request.user.user_type == "student":
            return obj.school in [
                cls.school for cls in request.user.class_students.all()
            ]

        return False


class IsTeacherOfClass(BasePermission):
    def has_permission(self, request, view):
        class_id = request.data.get("class_id")
        if not class_id:
            return False

        try:
            class_obj = Class.objects.get(id=class_id)
            return request.user == class_obj.teacher
        except Class.DoesNotExist:
            return False


class IsManagerOfSchool(BasePermission):
    def has_permission(self, request, view):
        school_id = request.data.get("school_id")
        if not school_id:
            return False

        try:
            school = School.objects.get(id=school_id)
            return request.user == school.manager
        except School.DoesNotExist:
            return False


class CanViewNews(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.class_obj:
            if request.user.user_type == "student":
                return obj.class_obj.students.filter(id=request.user.id).exists()
            elif request.user.user_type == "teacher":
                return obj.class_obj.teacher == request.user
            elif request.user.user_type == "Manager":
                return obj.class_obj.school.manager == request.user
        elif obj.school:
            if request.user.user_type == "student":
                return obj.school in [
                    cls.school for cls in request.user.class_students.all()
                ]
            elif request.user.user_type == "teacher":
                return obj.school in [
                    cls.school for cls in request.user.class_teacher.all()
                ]
            elif request.user.user_type == "manager":
                return obj.school.manager == request.user
        return False


class IsCreatorOrManager(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.creator == request.user:
            return True
        if (
            request.user.user_type == "manager"
            and obj.school == request.user.school_manager
        ):
            return True

        return False
