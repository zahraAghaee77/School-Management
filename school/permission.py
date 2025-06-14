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


class IsTeacherOfClass(BasePermission):
    def has_permission(self, request, view):
        class_id = view.kwargs.get("pk")
        if not class_id:
            return False
        try:
            class_obj = Class.objects.get(id=class_id)
            return request.user == class_obj.teacher
        except Class.DoesNotExist:
            return False


class IsManagerOfSchool(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "school_manager")


class IsManagerOfClass(BasePermission):
    def has_permission(self, request, view):
        class_id = view.kwargs.get("pk")
        if not class_id:
            return False
        try:
            class_obj = Class.objects.get(id=class_id)
            return request.user == class_obj.school.manager
        except Class.DoesNotExist:
            return False


class IsStudentOfClass(BasePermission):
    def has_permission(self, request, view):
        class_id = view.kwargs.get("pk")
        if not class_id:
            return False

        try:
            class_obj = Class.objects.get(id=class_id)
            return class_obj.students.filter(id=request.user.id).exists()
        except Class.DoesNotExist:
            return False
