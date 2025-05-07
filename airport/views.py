from django.shortcuts import render
from rest_framework import viewsets

from airport.models import (
    Airport,
    Airplane,
    AirplaneType,
    Route,
    Flight,
    Order,
    Ticket,
    Crew,
)
from airport.serializers import (
    AirportSerializer,
    AirplaneSerializer,
    AirplaneTypeSerializer,
    RouteSerializer,
    FlightSerializer,
    OrderSerializer,
    TicketSerializer,
    CrewSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    FlightListSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer


class AirPlaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        "route__source",
        "route__destination",
        "airplane",
    ).prefetch_related("members")
    serializer_class = FlightSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return FlightListSerializer
        return FlightSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("user")
    serializer_class = OrderSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("order", "flight")
    serializer_class = TicketSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer