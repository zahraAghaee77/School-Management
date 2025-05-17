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
