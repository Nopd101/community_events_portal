from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Create default groups: Admin, Organizer, Attendee"

    def handle(self, *args, **options):
        for name in ["Admin", "Organizer", "Attendee"]:
            Group.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("Groups ready: Admin, Organizer, Attendee"))
