from django.db import models


class Airport(models.Model):
    name = models.CharField(max_length=80, unique=True)
    closest_big_city = models.CharField(max_length=80)

    def __str__(self):
        return self.name
