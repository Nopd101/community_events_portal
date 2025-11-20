from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    class Roles(models.TextChoices):
        ADMIN = "admin", "Admin"
        ORGANIZER = "organizer", "Organizer"
        ATTENDEE = "attendee", "Attendee"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Roles.choices, default="attendee")
    phone = models.CharField(max_length=30, blank=True)
    organization = models.CharField(max_length=150, blank=True)
    position = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.role})"