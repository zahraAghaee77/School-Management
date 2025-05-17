from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register("users", UserViewSet)


urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("", include(router.urls)),
    path("logout/", LogoutAPIView.as_view()),
]
