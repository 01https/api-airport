from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    AirplaneViewSet,
    AirPlaneTypeViewSet
)

router = routers.DefaultRouter()
router.register("airports", AirportViewSet, basename="airports")
router.register("airplanes", AirplaneViewSet, basename="airplanes")
router.register("airplanes-type", AirPlaneTypeViewSet, basename="airplanes-type")

urlpatterns = [
    path("", include(router.urls))
]

app_name = "airport"