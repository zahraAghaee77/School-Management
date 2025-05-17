from datetime import timezone

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


class IsTeacherOfLesson(BasePermission):
    def has_permission(self, request, view):
        lesson_id = request.data.get("lesson_id")
        if not lesson_id:
            return False

        try:
            lesson = Lesson.objects.get(id=lesson_id)
            return request.user == lesson.class_lessons.first().teacher
        except Lesson.DoesNotExist:
            return False


class CanUpdateAssignment(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.lesson.class_lessons.first().teacher != request.user:
            return False

        return obj.deadline > timezone.now()


class CanAddAnswer(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.class_obj.teacher != request.user:
            return False

        return obj.deadline < timezone.now()


class CanSubmitOrUpdateSolution(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.student != request.user:
            return False
        return obj.assignment.deadline > timezone.now()


class IsTeacherOfAssignment(BasePermission):

    def has_permission(self, request, view):
        assignment_id = view.kwargs.get("pk")
        try:
            assignment = Assignment.objects.get(id=assignment_id)
            return assignment.class_obj.teacher == request.user
        except Assignment.DoesNotExist:
            return False


class CanGradeSolution(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.assignment.class_obj.teacher != request.user:
            return False

        return obj.assignment.deadline < timezone.now()


class CanViewSolution(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.user_type == "teacher":
            return obj.assignment.class_obj.teacher == request.user
        elif request.user.user_type == "student":
            return obj.student == request.user
        return False
