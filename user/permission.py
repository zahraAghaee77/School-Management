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
