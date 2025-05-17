from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register("classes", ClassViewSet)
router.register("schools", SchoolViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
