from django.contrib.auth.models import User
from django.db import models


class Run(models.Model):
    STATUS_INIT = 'init'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_FINISHED = 'finished'

    STATUS_CHOICES = (
        (STATUS_INIT, 'init'),
        (STATUS_IN_PROGRESS, 'in_progress'),
        (STATUS_FINISHED, 'finished'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_INIT)
    distance = models.DecimalField(max_digits=20, decimal_places=4, default=0)

    def __str__(self):
        return f'Забег {self.id}: {self.status}'


class AthleteInfo(models.Model):
    weight = models.IntegerField(null=True)
    goals = models.CharField(max_length=1024, null=True, blank=True)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)


class Challenge(models.Model):
    full_name = models.CharField(max_length=255, blank=False, null=False)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.athlete}: {self.full_name}'


class Position(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    latitude = models.DecimalField(decimal_places=4, max_digits=6)
    longitude = models.DecimalField(decimal_places=4, max_digits=7)

    def __str__(self):
        return f'{self.run}, lat: {self.latitude} long: {self.longitude}'


class CollectibleItem(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    uid = models.CharField(max_length=8, blank=False, null=False)
    latitude = models.DecimalField(decimal_places=4, max_digits=6)
    longitude = models.DecimalField(decimal_places=4, max_digits=7)
    picture = models.URLField()
    value = models.PositiveSmallIntegerField(null=False)

    def __str__(self):
        return f'{self.name}: lat - {self.latitude}, long - {self.longitude}'
