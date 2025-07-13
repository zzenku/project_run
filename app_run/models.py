from django.contrib.auth.models import User
from django.db import models


class Run(models.Model):
    STATUS_CHOICES = (
        (0, 'init'),
        (1, 'in_progress'),
        (2, 'finished'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)

    def __str__(self):
        return f'Забег {self.id}: {self.status}'
