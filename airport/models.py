from django.db import models


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