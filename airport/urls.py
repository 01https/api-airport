from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    AirplaneViewSet,
    AirPlaneTypeViewSet,
    RouteViewSet,
    FlightViewSet, OrderViewSet,
)

router = routers.DefaultRouter()
router.register("port", AirportViewSet, basename="port")
router.register("airplanes", AirplaneViewSet, basename="airplanes")
router.register("airplanes-type", AirPlaneTypeViewSet, basename="airplanes-type")
router.register("route", RouteViewSet, basename="routes")
router.register("flight", FlightViewSet, basename="flights")
router.register("order", OrderViewSet, basename="orders")

urlpatterns = [
    path("", include(router.urls))
]

app_name = "airport"