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

    def __str__(self):
        return f'Забег {self.id}: {self.status}'
