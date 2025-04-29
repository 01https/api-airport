from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    AirplaneViewSet
)

router = routers.DefaultRouter()
router.register("airports", AirportViewSet, basename="airports")
router.register("airplanes", AirplaneViewSet, basename="airplanes")

urlpatterns = [
    path("", include(router.urls))
]

app_name = "airport"