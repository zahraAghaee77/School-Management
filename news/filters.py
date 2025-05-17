import django_filters
from rest_framework import filters

from .models import *


class TeacherHasAccessFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        pass
