from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import *
from rest_framework.permissions import *
from rest_framework.response import *
from rest_framework.views import *
from rest_framework_simplejwt.tokens import RefreshToken

from school.models import *
from school.serializer import *

from .models import User
from .permission import *
from .serializer import *


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == ["update", "partial_update"]:
            return UpdateBioSerializer
        return super().get_serializer_class()

    @swagger_auto_schema(operation_description="Activate user by admin.")
    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[IsAdminUser],
    )
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response(
            {"message": "User activated successfully."},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(operation_description="See all lessons of teacher.")
    @action(
        detail=False,
        methods=["get"],
        url_name="my-lessons",
        url_path="my-lessons",
        permission_classes=[IsTeacher],
    )
    def my_lessons(self, request):

        # URL: /users/my_lessons/

        try:
            lessons = Lesson.objects.filter(
                class_lessons__teacher=request.user
            ).distinct()
            serializer = LessonSerializer(lessons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_description="See all lessons of student.")
    @action(
        detail=False,
        methods=["get"],
        url_name="my-lessons",
        url_path="my-lessons",
        permission_classes=[IsStudent],
    )
    def my_lessons(self, request):

        # URL: /users/my_lessons/

        try:
            lessons = Lesson.objects.filter(
                class_lessons__students=request.user
            ).distinct()
            serializer = LessonSerializer(lessons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        if self.request.user.is_staff:
            return super().list(request, *args, **kwargs)
        return Response(
            {"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def create(self, request, *args, **kwargs):
        if self.request.user.is_staff:
            return super().create(request, *args, **kwargs)
        return Response(
            {"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        if self.request.user.is_staff:
            return super().destroy(request, *args, **kwargs)
        return Response(
            {"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class UserRegistrationView(APIView):
    """
    POST request body:
    {
        "username": "bla",
        "first_name": "bla",
        "last_name": "bla",
        "email": "bla@example.com",
        "national_id": "1234567890",
        "user_type": "student",
        "password": "bla",
        "confirm_password": "bla"
    }
    """

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "data": serializer.data,
                    "message": "You registered successfuly, please wait for admin approval.",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(generics.GenericAPIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response(
                {"detail": "There is a problem with logging out."},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""
class ActivateUserView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            serializer = UserSerializer(user)
            return Response(
                {"message": "User activated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )


            
class UpdateProfileViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateBioSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def list(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


"""
