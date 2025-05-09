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
        return f"{self.source}, {self.destination}"


class Flight(models.Model):
    route = models.ForeignKey("Route", on_delete=models.PROTECT)
    airplane = models.ForeignKey("Airplane", on_delete=models.PROTECT)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    members = models.ManyToManyField("Crew", related_name="crews")

    def __str__(self):
        return f"{self.route} - {self.airplane}"

    @property
    def available_seats(self):
        total_seats = self.airplane.rows * self.airplane.seats_in_row

        taken_seats = self.tickets.count()

        return total_seats - taken_seats

    @property
    def taken_seats_detail(self):
        return [
            {"row": ticket.row, "seat": ticket.seat}
            for ticket in Ticket.objects.all()
        ]

    @property
    def taken_seats_list(self):
        return self.tickets.count()


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.created_at}, {self.user}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey("Flight", on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="tickets")

    def __str__(self):
        return f"{self.row}, {self.seat}, {self.order}"


class Crew(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
