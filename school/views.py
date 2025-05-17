from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import *
from rest_framework.permissions import *
from rest_framework.response import *
from rest_framework.views import *
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import *
from user.serializer import *

from .filters import *
from .models import *
from .permission import *
from .serializer import *


class SchoolViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdminUser]
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return School.objects.all()
        elif user.user_type == "manager":
            return School.objects.filter(manager=user)
        return School.objects.none()

    @swagger_auto_schema(operation_description="See all students of school by manager")
    @action(
        detail=True,
        methods=["get"],
        permission_classes=[IsManagerOfSchool],
    )
    def students(self, requset, pk=None):

        # URL: /schools/{school_id}/students/

        try:
            school = self.get_object()
            students = User.objects.filter(
                class_students__school=school, user_type="student"
            ).distinct()
            serializer = UserSerializer(students, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except School.DoesNotExist:
            return Response(
                {"detail": "School not found."}, status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(operation_description="See all lessons of school by manager.")
    @action(
        detail=True,
        methods=["get"],
        permission_classes=[IsManagerOfSchool],
    )
    def lessons(self, request, pk=None):

        # URL: /schools/{school_id}/lessons/

        try:
            school = self.get_object()
            lessons = Lesson.objects.filter(class_lessons__school=school).distinct()
            serializer = LessonSerializer(lessons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except School.DoesNotExist:
            return Response(
                {"detail": "The school not found."}, status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(operation_description="See all teachers of school by manager.")
    @action(detail=True, methods=["get"], permission_classes=[IsManagerOfSchool])
    def teachers(self, request, pk=None):

        # URL: /schools/{school_id}/teachers/

        try:
            school = self.get_object()
            teachers = User.objects.filter(
                class_teacher__school=school, user_type="teacher"
            ).distinct()
            serializer = UserSerializer(teachers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except School.DoesNotExist:
            return Response(
                {"detail": "The school not found."}, status=status.HTTP_404_NOT_FOUND
            )


class ClassViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClassSerializer
    queryset = Class.objects.all()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsStudentReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CreateClassSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Class.objects.all()
        if user.user_type == "teacher":
            return Class.objects.filter(teacher=self.request.user)
        if user.user_type == "student":
            return Class.objects.filter(students=user)
        if user.user_type == "manager":
            return Class.objects.filter(school__manager=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        return super().perform_create(serializer)

    def create(self, request, *args, **kwargs):
        if not (request.user.is_staff):
            raise PermissionDenied("You do not have permission to create classes.")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not (request.user.is_staff):
            raise PermissionDenied("You do not have permission to update classes.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not (request.user.is_staff):
            raise PermissionDenied("You do not have permission to delete classes.")
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Add student to a class by teacher.")
    @action(
        detail=True,
        methods=["post"],
        url_path="add-student",
        url_name="add-student",
        permission_classes=[IsTeacherOfClass],
    )
    def add_student(self, requset, pk=None):
        """

        URL: /classes/{class_id}/add-student/
        Request Body: {"national_id": national_id}

        """
        try:
            class_obj = self.get_object()
            national_id = requset.data.get("national_id")
            if not national_id:
                return Response(
                    {"detail": "The national id is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                student = User.objects.get(national_id=national_id, user_type="student")
            except User.DoesNotExist:
                return Response(
                    {
                        "detail": f"The student with this national_id = {national_id} does not exist or is not a student."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            if class_obj.students.filter(id=student.id).exists():
                return Response(
                    {"detail": "The student was already in this class."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            class_obj.students.add(student)
            return Response(
                {"detail": "The student was added successfully."},
                status=status.HTTP_200_OK,
            )
        except Class.DoesNotExist:
            return Response(
                {"detail": "This class was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(
        operation_description="Remove student from a class by teacher."
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="remove-student",
        url_name="remove-student",
        permission_classes=[IsTeacherOfClass],
    )
    def remove_student(self, requset, pk=None):
        """

        URL: /classes/{class_id}/remove-student/
        Request Body: {"national_id": national_id}

        """
        try:
            class_obj = self.get_object()
            national_id = requset.data.get("national_id")
            if not national_id:
                return Response(
                    {"detail": "The national id is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                student = User.objects.get(national_id=national_id, user_type="student")
            except User.DoesNotExist:
                return Response(
                    {
                        "detail": f"The student with this national_id = {national_id} does not exist or is not a student."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            if not class_obj.students.filter(id=student.id).exists():
                return Response(
                    {"detail": "The student was not in this class."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            class_obj.students.remove(student)
            return Response(
                {"detail": "The student was removed from class successfully."},
                status=status.HTTP_200_OK,
            )
        except Class.DoesNotExist:
            return Response(
                {"detail": "This class was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(operation_description="See students of a class by teacher.")
    @action(
        detail=True,
        methods=["get"],
        permission_classes=[IsTeacherOfClass],
    )
    def students(self, requset, pk=None):
        # URL: /classes/{class_id}/students/
        try:
            class_obj = self.get_object()
            students_class = class_obj.students.all()
            serializer = UserSerializer(students_class, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Class.DoesNotExist:
            return Response(
                {"detail": "This class was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(operation_description="Add lesson to a class by manager.")
    @action(
        detail=True,
        methods=["post"],
        url_path="add-lesson",
        url_name="add-lesson",
        permission_classes=[IsManagerOfClass],
    )
    def add_lesson(self, requset, pk=None):
        """

        URL: /classes/{class_id}/add-lesson/
        Request Body: {"name": "Lesson Name"}

        """
        try:
            class_obj = self.get_object()
            lesson_name = requset.data.get("name")
            if not lesson_name:
                return Response(
                    {"detail": "The lesson name is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            lesson, created = Lesson.objects.get_or_create(name=lesson_name)
            if class_obj.lessons.filter(id=lesson.id).exits():
                return Response(
                    {"detail": "The lesson name is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            class_obj.lessons.add(lesson)
            return Response(
                {"detail": "This lesson was added successfully."},
                status=status.HTTP_200_OK,
            )
        except Class.DoesNotExist:
            return Response(
                {"detail": "This class was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(operation_description="List all lessons of a class.")
    @action(
        detail=True,
        methods=["get"],
        permission_classes=[IsTeacherOfClass | IsStudentOfClass | IsManagerOfClass],
    )
    def lessons(self, request, pk=None):

        # URL: /classes/{class_id}/lessons/

        try:
            class_obj = self.get_object()
            lessons = class_obj.lessons.all()
            serializer = LessonSerializer(lessons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Class.DoesNotExist:
            return Response(
                {"detail": "Class not found."}, status=status.HTTP_404_NOT_FOUND
            )
