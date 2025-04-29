from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    AirplaneViewSet,
    AirPlaneTypeViewSet,
    RouteViewSet,
    FlightViewSet,
)

router = routers.DefaultRouter()
router.register("air", AirportViewSet, basename="air")
router.register("airplanes", AirplaneViewSet, basename="airplanes")
router.register("airplanes-type", AirPlaneTypeViewSet, basename="airplanes-type")
router.register("route", RouteViewSet, basename="routes")
router.register("flight", FlightViewSet, basename="flights")

urlpatterns = [
    path("", include(router.urls))
]

app_name = "airport"