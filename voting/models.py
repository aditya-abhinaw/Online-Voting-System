
from django.conf import settings
from django.db import models
from django.utils import timezone


class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    @property
    def is_open(self):
        now = timezone.now()
        return (
            self.is_active
            and self.start_time <= now <= self.end_time
        )

    def __str__(self):
        return self.title


class Candidate(models.Model):
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name='candidates'
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Vote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE
    )
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'election'],
                name='unique_vote_per_user_per_election'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.candidate}'
