from django.urls import path, include
from rest_framework import routers

from games.views import GamesViewSet

router = routers.DefaultRouter()
router.register(r"games", GamesViewSet, basename="games")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
]
