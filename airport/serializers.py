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
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    source_airport = serializers.CharField(source="source.name")
    destination_airport = serializers.CharField(source="destination.name")

    class Meta:
        model = Route
        fields = (
            "id",
            "source_airport",
            "destination_airport",
            "distance"
        )


class RouteDetailSerializer(RouteListSerializer):
    source_closest_big_city = serializers.CharField(
        source="source.closest_big_city"
    )
    destination_closest_big_city = serializers.CharField(
        source="destination.closest_big_city"
    )

    class Meta:
        model = Route
        fields = (
            "id",
            "source_airport",
            "destination_airport",
            "source_closest_big_city",
            "destination_closest_big_city",
            "distance",
        )


class FlightSerializer(serializers.ModelSerializer):
    route = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.select_related("source", "destination")
    )
    departure = serializers.SerializerMethodField()
    arrival = serializers.SerializerMethodField()
    airplane = serializers.SlugRelatedField(
        queryset=Airplane.objects.all(),
        slug_field="name"
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure",
            "arrival",
            "departure_time",
            "arrival_time",
            "members"
        )

    def get_departure(self, obj):
        return obj.route.source.name

    def get_arrival(self, obj):
        return obj.route.destination.name

class FlightListSerializer(FlightSerializer):
    members = serializers.SlugRelatedField(
        many=True,
        slug_field="full_name",
        read_only=True
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

