from rest_framework import serializers
from django.db import transaction

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


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(
        queryset=AirplaneType.objects.all(),
        slug_field="name",
    )

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
        )


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        queryset=Airport.objects.all(),
        slug_field="closest_big_city"
    )
    destination = serializers.SlugRelatedField(
        queryset=Airport.objects.all(),
        slug_field="closest_big_city"
    )

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class FlightSerializer(serializers.ModelSerializer):
    departures = serializers.CharField(source="route.source.closest_big_city", read_only=True)
    arrivals = serializers.CharField(source="route.destination.closest_big_city", read_only=True)
    members = serializers.StringRelatedField(many=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departures",
            "arrivals",
            "departure_time",
            "arrival_time",
            "members",
        )

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order

