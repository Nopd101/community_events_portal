from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from datetime import date, time, timedelta
from accounts.models import Profile
from events.models import Event


class Command(BaseCommand):

    def handle(self, *args, **options):
        User = get_user_model()

        # Seeding GROUPS
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        organizer_group, _ = Group.objects.get_or_create(name="Organizer")
        attendee_group, _ = Group.objects.get_or_create(name="Attendee")

        admin_group.permissions.clear()
        organizer_group.permissions.clear()
        attendee_group.permissions.clear()

        def get_perms(app_label, model_name, actions):
            """
            app_label: e.g. 'events', 'accounts'
            model_name: lowercase model name, e.g. 'event', 'profile'
            actions: list like ['add', 'change', 'view']
            """
            ct = ContentType.objects.get(app_label=app_label, model=model_name)
            codenames = [f"{action}_{model_name}" for action in actions]
            return Permission.objects.filter(content_type=ct, codename__in=codenames)

        #  ADMIN PERMISSIONS 
        admin_group.permissions.set(Permission.objects.all())

        #  ORGANIZER PERMISSIONS 
        organizer_perms = []
        organizer_perms += list(get_perms("events", "event", ["add", "change", "delete", "view"]))
        organizer_perms += list(get_perms("events", "participation", ["view"]))
        organizer_perms += list(get_perms("events", "feedback", ["view"]))
        organizer_perms += list(get_perms("events", "eventcapacity", ["view", "change"]))
        organizer_perms += list(get_perms("accounts", "profile", ["view", "change"]))
        organizer_group.permissions.set(organizer_perms)

        # ATTENDEE PERMISSIONS
        attendee_perms = []
        attendee_perms += list(get_perms("events", "event", ["view"]))
        attendee_perms += list(get_perms("events", "participation", ["add", "view"]))
        attendee_perms += list(get_perms("events", "feedback", ["add", "view"]))
        attendee_perms += list(get_perms("accounts", "profile", ["view", "change"]))
        attendee_group.permissions.set(attendee_perms)

        self.stdout.write(self.style.SUCCESS("Groups and permissions seeded."))

        # THIS IS THE PART FOR CREATION OF USERS & PROFILES

        # Creating ADMINS
        admins_data = [
            {
                "username": "miyuki_ando",
                "first_name": "Miyuki",
                "last_name": "Ando",
                "email": "miyuki.ando@example.com",
                "password": "Miyuki123!",
            },
            {
                "username": "daryl_cruz",
                "first_name": "Daryl",
                "last_name": "Cruz",
                "email": "daryl.cruz@example.com",
                "password": "Daryl123!",
            },
        ]

        admin_users = []
        for data in admins_data:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "is_staff": True,
                    "is_superuser": True,
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()
            admin_group.user_set.add(user)
            Profile.objects.get_or_create(
                user=user,
                defaults={
                    "role": "admin",
                    "phone": "09170000000",
                    "organization": "System Admin Office",
                    "position": "Administrator",
                    "bio": "Seeded admin account.",
                    "website": "",
                    "verified": True,
                },
            )
            admin_users.append(user)

        # Creating ORGANIZERS
        organizers_data = [
            {
                "username": "luther_delacruz",
                "first_name": "Luther",
                "last_name": "Dela Cruz",
                "email": "luther.delacruz@example.com",
                "password": "Luther123!",
            },
            {
                "username": "jr_eleazar",
                "first_name": "JR",
                "last_name": "Eleazar",
                "email": "jr.eleazar@example.com",
                "password": "JREleazar123!",
            },
        ]

        organizer_users = []
        for data in organizers_data:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "is_staff": True,
                    "is_superuser": False,
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()
            organizer_group.user_set.add(user)
            Profile.objects.get_or_create(
                user=user,
                defaults={
                    "role": "organizer",
                    "phone": "09171111111",
                    "organization": "Community Org",
                    "position": "Event Organizer",
                    "bio": "Seeded organizer account.",
                    "website": "",
                    "verified": True,
                },
            )
            organizer_users.append(user)

        # Creating ATTENDEES
        attendees_data = [
            {
                "username": "miguel_eugenio",
                "first_name": "Miguel",
                "last_name": "Eugenio",
                "email": "miguek.eugenio@example.com",
                "password": "Miguel123!",
            },
            {
                "username": "john_doe",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password": "JohnDoe123!",
            },
        ]

        attendee_users = []
        for data in attendees_data:
            user, created = User.objects.get_or_create(
                username=data["username"],
                defaults={
                    "email": data["email"],
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "is_staff": False,
                    "is_superuser": False,
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()
            attendee_group.user_set.add(user)
            Profile.objects.get_or_create(
                user=user,
                defaults={
                    "role": "attendee",
                    "phone": "09172222222",
                    "organization": "",
                    "position": "",
                    "bio": "Seeded attendee account.",
                    "website": "",
                    "verified": False,
                },
            )
            attendee_users.append(user)

        self.stdout.write(self.style.SUCCESS("Users and profiles seeded (2 per role)."))

        # Seeding Events For Initial View of the Website
        current_year = date.today().year
        base_date = date(current_year, 12, 15)

        event_titles = [
            "Sir Burgos' Seminar",
            "Coca Cola's Music Festival",
            "Samsung's Company Seminar",
            "Vegan Feast",
            "Wish 107's Concert",
            "Health is Wealth Program",
            "United Nations",
            "Run It Down",
            "Costume Party",
            "Job Hunting",
        ]

        for index, title in enumerate(event_titles):
            event_date = base_date + timedelta(days=index)

            if index < 5:
                organizer = organizer_users[0]
                local_idx = index
            else:
                organizer = organizer_users[1]
                local_idx = index - 5

            status = "approved" if local_idx < 3 else "pending"

            event, created = Event.objects.get_or_create(
                title=title,
                organizer=organizer,
                date=event_date,
                defaults={
                    "start_time": time(9, 0),
                    "end_time": time(11, 0),
                    "location": "Community Hall",
                    "short_description": f"Auto-seeded event: {title}.",
                    "status": status,
                },
            )

            image_name = f"events/images/event_{index + 1}.jpg"
            if not event.image or event.image.name != image_name:
                event.image.name = image_name
                event.save()

        self.stdout.write(self.style.SUCCESS("Events seeded (5 per organizer, 3 approved / 2 pending each, with images)."))
        self.stdout.write(self.style.SUCCESS("Seeding complete."))
