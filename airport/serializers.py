from drf_spectacular.utils import extend_schema_field
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
    airplane = serializers.PrimaryKeyRelatedField(
        queryset=Airplane.objects.all()
    )
    departure = serializers.SerializerMethodField()
    airplane_type = serializers.SerializerMethodField()
    seat_in_row = serializers.SerializerMethodField()
    row = serializers.SerializerMethodField()
    arrival = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "airplane_type",
            "row",
            "seat_in_row",
            "available_seats",
            "departure",
            "arrival",
            "departure_time",
            "arrival_time",
            "distance",
        )

    @extend_schema_field(str)
    def get_departure(self, obj) -> str:
        return obj.route.source.name

    @extend_schema_field(str)
    def get_arrival(self, obj) -> str:
        return obj.route.destination.name

    @extend_schema_field(int)
    def get_distance(self, obj) -> int:
        return obj.route.distance

    @extend_schema_field(str)
    def get_airplane_type(self, obj) -> str:
        return obj.airplane.airplane_type.name

    @extend_schema_field(int)
    def get_seat_in_row(self, obj) -> int:
        return obj.airplane.seats_in_row

    @extend_schema_field(int)
    def get_row(self, obj) -> int:
        return obj.airplane.rows

    @extend_schema_field(int)
    def get_available_seats(self, obj) -> int:
        return obj.available_seats

class FlightListSerializer(FlightSerializer):
    airplane = serializers.SlugRelatedField(
        queryset=Airplane.objects.all(),
        slug_field="name",
        many=False
    )
    taken_seats = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "airplane_type",
            "taken_seats",
            "available_seats",
            "departure",
            "arrival",
            "departure_time",
            "arrival_time",
        )

    @extend_schema_field(int)
    def get_taken_seats(self, obj) -> int:
        return obj.taken_seats_list


class FlightRetrieveSerializer(FlightListSerializer):
    members = serializers.SlugRelatedField(
        many=True,
        slug_field="full_name",
        read_only=True
    )
    taken_seats = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "airplane_type",
            "row",
            "seat_in_row",
            "departure",
            "arrival",
            "departure_time",
            "arrival_time",
            "distance",
            "members",
            "available_seats",
            "taken_seats"
        )

    @extend_schema_field(list[dict[str, int]])
    def get_taken_seats(self, obj):
        return obj.taken_seats_detail


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")

    def validate(self, attrs):
        flight = attrs["flight"]
        seat = attrs["seat"]
        row = attrs["row"]
        airplane = flight.airplane

        errors = {}

        if Ticket.objects.filter(flight=flight, row=row, seat=seat).exists():
            errors["taken_seats"] = f"Seat {row}-{seat} is already occupied on this flight"

        if seat < 1 or seat > airplane.seats_in_row:
            errors["seat"] = f"The seat number {seat} is out of range (1 - {airplane.seats_in_row})"

        if row < 1 or row > airplane.rows:
            errors["row"] = f"The row number {row} is out of range (1 - {airplane.rows})"

        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class TicketRetrieveForOrderSerializer(TicketSerializer):
    flight = FlightListSerializer()

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "tickets")
        read_only_fields = ("user",)

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    user = serializers.CharField(source="user.email")


class OrderRetrieveSerializer(OrderListSerializer):
    tickets = TicketRetrieveForOrderSerializer(many=True, read_only=False, allow_empty=False)