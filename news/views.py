from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import *
from rest_framework.permissions import *
from rest_framework.response import *
from rest_framework.views import *
from rest_framework_simplejwt.tokens import RefreshToken

from school.models import *
from user.models import *
from user.serializer import *

from .models import *
from .permission import *
from .serializer import *


class NewsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsTeacherOfClass, IsManagerOfSchool]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsCreatorOrManager]
        else:
            permission_classes = [CanViewNews]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        class_id = self.request.data.get("class_id")
        school_id = self.request.data.get("school_id")

        if class_id:
            class_obj = Class.objects.get(id=class_id)
            serializer.save(creator=self.request.user, class_obj=class_obj)
        elif school_id:
            school = School.objects.get(id=school_id)
            serializer.save(creator=self.request.user, school=school)
        else:
            raise ValueError("Either 'class_obj' or 'school' must be provided.")

        return super().perform_create(serializer)

    def get_serializer_class(self):
        if self.action == "manager_add_news":
            return ManagerNewsSerializer
        return super().get_serializer_class()


"""   
class ManagerNewsAPI(APIView):
    permission_classes = [IsManager]

    def post(self, request):
        serializer = ManagerNewsSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(
                {"massage": "News was created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            news = News.objects.get(id=pk, creator=request.user)
        except News.DoesNotExist:
            return Response(
                {
                    "error": "The news was not found or you do not have permission to update it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ManagerNewsSerializer(news, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"massage": "News was updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class TeacherAllNewsAPI(APIView):

    permission_classes = [IsTeacher]

    def get(self, request):
        own_news = News.objects.filter(creator=request.user)

        all_classes = Class.objects.filter(teacher=request.user)
        schools = {class_item.school for class_item in all_classes}
        school_news = News.objects.filter(
            creator__user_type="manager", school__in=schools
        )

        all_news = own_news.union(school_news).order_by("created_at")
        serializer = NewsSerializer(all_news, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class TeacherNewsAPI(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        own_news = News.objects.filter(creator=request.user)
        serializer = NewsSerializer(own_news, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, news_id):
        all_classes = Class.objects.filter(teacher=request.user)
        schools = {class_item.school for class_item in all_classes}

        try:
            news = News.objects.get(id=news_id)
            if news.creator == request.user or (
                news.school in schools and news.creator.user_type == "manager"
            ):
                serializer = NewsSerializer(news)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "You do not have permission to access this news."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        except News.DoesNotExist:
            return Response(
                {"error": "The news was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        serializer = TeacherNewsSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(
                {"massage": "News created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, news_id):
        try:
            news = News.objects.get(id=news_id, creator=request.user)
        except News.DoesNotExist:
            return Response(
                {
                    "error": "The news was not found or you do not have permission to update it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TeacherNewsSerializer(news, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"massage": "News was updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentNewsAPI(APIView):
    permission_classes = [IsStudent]

    def get(self, request):

        student = request.user
        student_classes = Class.objects.filter(students=student)
        student_schools = {class_student.school for class_student in student_classes}
        student_school_news = News.objects.filter(
            school__in=student_schools, creator__user_type="manager"
        )
        student_class_news = News.objects.filter(class_obj__in=student_classes)

        all_news = student_class_news.union(student_school_news).orderBy("created_at")
        serializer = NewsSerializer(all_news, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, news_id):
        student = request.user
        student_classes = Class.objects.filter(students=student)
        student_schools = {class_student.school for class_student in student_classes}

        try:
            news = News.objects.filter(id=news_id)
            if news.class_obj in student_classes or (
                news.school in student_schools and news.creator.user_type == "manager"
            ):
                serializer = NewsSerializer(news)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "You do not have permission to access this news."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except News.DoesNotExist:
            return Response(
                {"error": "The news was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
"""
