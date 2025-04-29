from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    AirplaneViewSet,
    AirPlaneTypeViewSet,
    RouteViewSet,
    FlightViewSet, OrderViewSet, TicketViewSet, CrewViewSet,
)

router = routers.DefaultRouter()
router.register("port", AirportViewSet, basename="port")
router.register("airplanes", AirplaneViewSet, basename="airplanes")
router.register("airplanes-type", AirPlaneTypeViewSet, basename="airplanes-type")
router.register("routes", RouteViewSet, basename="routes")
router.register("flights", FlightViewSet, basename="flights")
router.register("orders", OrderViewSet, basename="orders")
router.register("tickets", TicketViewSet, basename="tickets")
router.register("crews", CrewViewSet, basename="crews")

urlpatterns = [
    path("", include(router.urls))
]

app_name = "airport"