from django.db import models
from django.conf import settings


class Airport(models.Model):
    name = models.CharField(max_length=80, unique=True)
    closest_big_city = models.CharField(max_length=80)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=80, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey("AirplaneType", on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class AirplaneType(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey("Airport", on_delete=models.PROTECT, related_name="departures")
    destination = models.ForeignKey("Airport", on_delete=models.PROTECT, related_name="arrivals")
    distance = models.IntegerField()

    def __str__(self):
        return self.source, self.destination


class Flight(models.Model):
    route = models.ForeignKey("Route", on_delete=models.PROTECT)
    airplane = models.ForeignKey("Airplane", on_delete=models.PROTECT)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return self.route, self.airplane


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return self.created_at, self.user


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey("Flight", on_delete=models.PROTECT)
    order = models.ForeignKey("Order", on_delete=models.PROTECT)

    def __str__(self):
        return self.row, self.seat, self.order