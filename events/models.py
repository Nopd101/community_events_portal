from django.db import models
from django.conf import settings


class Event(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("declined", "Declined"),
        ("full", "Full"),
    ]
    title = models.CharField(max_length=200)
    date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    short_description = models.TextField(blank=True)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_events",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return self.title


class Participation(models.Model):
    """Records that a user joined an approved event."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="participants")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "event")

    def __str__(self):
        return f"{self.user.username} → {self.event.title}"


class Feedback(models.Model):
    """1–5 rating + optional comment from an attendee for an event they joined."""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="feedbacks")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("event", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event.title} - {self.user.username} ({self.rating}★)"