from django.db import models


class Location(models.Model):

    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=256)

    class Meta:
        unique_together = ('latitude', 'longitude',)

    def __str__(self):
        return self.address
