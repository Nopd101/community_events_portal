from django.db import models
from django.conf import settings
import uuid
import os

def event_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join("events", "images", new_filename)

class Event(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("declined", "Declined"),
        ("full", "Full"),
    ]
    title = models.CharField(max_length=200)
    date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    short_description = models.TextField(blank=True)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_events",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    image = models.ImageField(
        upload_to=event_image_upload_path,
        null=True,
        blank=True,
    )
    
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


class EventCapacity(models.Model):
    """
    Stores capacity info for an event:
    - max_participants: allowed max
    - current_participants: cached current count
    """
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name="capacity",
    )
    max_participants = models.PositiveIntegerField()
    current_participants = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.event.title} capacity ({self.current_participants}/{self.max_participants})"

    @property
    def is_full(self):
        return self.current_participants >= self.max_participants

    def refresh_current_participants(self):
        """
        Recalculate based on Participation records.
        Call this if you want a fresh count from DB.
        """
        self.current_participants = self.event.participants.count()
        self.save()

