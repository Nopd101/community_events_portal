from datetime import datetime, date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from .models import Event, Participation, Feedback, EventCapacity
from .forms import EventForm, FeedbackForm
from accounts.forms import UserProfileForm


User = get_user_model()

def user_role(user):
    """Return user’s role from Profile or default to attendee."""
    return getattr(getattr(user, "profile", None), "role", "attendee")


def allow(request, roles: set):
    """Check if the current user can view this page."""
    if request.user.is_superuser:
        return True
    if user_role(request.user) in roles:
        return True
    messages.error(request, "You are not allowed to view this page.")
    return False


#This are all for the attendee side

@login_required
def attendee_events(request):
    if not allow(request, {"attendee"}):
        return redirect("route_after_login")

    q = request.GET.get("q", "").strip()
    events = Event.objects.filter(status="approved")
    if q:
        events = events.filter(title__icontains=q)

    joined_qs = Participation.objects.filter(user=request.user)
    joined_ids = set(joined_qs.values_list("event_id", flat=True))

    total_joined = joined_qs.count()
    today = date.today()
    upcoming_joined = joined_qs.filter(event__date__gte=today).count()

    for e in events:
        feedbacks = Feedback.objects.filter(event=e)
        if feedbacks.exists():
            total = sum(f.rating for f in feedbacks)
            e.avg_rating = round(total / feedbacks.count(), 1)
            e.fb_count = feedbacks.count()
        else:
            e.avg_rating = "-"
            e.fb_count = 0

    return render(request, "events/attendee_events.html", {
        "events": events,
        "q": q,
        "joined_ids": joined_ids,
        "total_joined": total_joined,
        "upcoming_joined": upcoming_joined,
    })


@login_required
def attendee_my_events(request):
    """Events the attendee has registered for."""
    if not allow(request, {"attendee"}):
        return redirect("route_after_login")

    participations = (
        Participation.objects
        .filter(user=request.user)
        .select_related("event")
        .order_by("event__date")
    )

    events = []
    for p in participations:
        e = p.event
        feedbacks = Feedback.objects.filter(event=e)
        if feedbacks.exists():
            total = sum(f.rating for f in feedbacks)
            e.avg_rating = round(total / feedbacks.count(), 1)
            e.fb_count = feedbacks.count()
        else:
            e.avg_rating = "-"
            e.fb_count = 0
        events.append(e)

    return render(request, "events/attendee_my_events.html", {
        "events": events,
    })


@login_required
def attendee_profile_edit(request):
    if not allow(request, {"attendee"}):
        return redirect("route_after_login")

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("events:attendee_profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "events/attendee_profile.html", {
        "form": form,
    })


@login_required
def attendee_join_event(request, event_id):
    if not allow(request, {"attendee"}):
        return redirect("route_after_login")

    # Only allow joining approved events
    event = get_object_or_404(Event, pk=event_id, status="approved")

    # Ensure capacity exists
    capacity, created = EventCapacity.objects.get_or_create(
        event=event,
        defaults={
            "max_participants": 1,  # or some sensible default
            "current_participants": event.participants.count(),
        },
    )

    # 🔹 Use LIVE count instead of cached current_participants
    current_count = event.participants.count()

    # Check if full
    if current_count >= capacity.max_participants:
        messages.error(request, "This event is already full.")
        return redirect("events:attendee_events")

    # Prevent double-joining
    participation, created = Participation.objects.get_or_create(
        user=request.user,
        event=event,
    )

    if not created:
        messages.info(request, "You have already joined this event.")
        return redirect("events:attendee_events")

    # 🔹 Recalculate and sync cached current_participants
    capacity.current_participants = event.participants.count()
    capacity.save()

    messages.success(request, "You successfully joined this event.")
    return redirect("events:attendee_events")


@login_required
def attendee_leave_event(request, event_id):
    """Allow attendee to cancel registration if event is at least 7 days away."""
    if not allow(request, {"attendee"}):
        return redirect("route_after_login")

    # Only approved events can be left
    event = get_object_or_404(Event, pk=event_id, status="approved")

    participation = Participation.objects.filter(
        user=request.user,
        event=event,
    ).first()

    if not participation:
        messages.error(request, "You are not registered for this event.")
        return redirect("events:attendee_my_events")

    # Enforce 7-day rule
    if event.date:
        days_diff = (event.date - date.today()).days
        if days_diff < 7:
            messages.error(
                request,
                "You can only cancel registration at least 7 days before the event date.",
            )
            return redirect("events:attendee_my_events")

    # We expect POST from your template form
    if request.method != "POST":
        # Just redirect if someone hits the URL directly via GET
        return redirect("events:attendee_my_events")

    # Delete the participation
    participation.delete()

    # Update capacity if it exists
    try:
        capacity = event.capacity
    except EventCapacity.DoesNotExist:
        capacity = None

    if capacity:
        # sync cached count with real participants
        capacity.current_participants = event.participants.count()
        capacity.save()

        # if event was full and now has space, reopen it
        if event.status == "full" and capacity.current_participants < capacity.max_participants:
            event.status = "approved"
            event.save(update_fields=["status"])

    messages.success(request, "You have been unregistered from this event.")
    return redirect("events:attendee_my_events")


@login_required
def feedback_create(request, event_id):
    if not allow(request, {"attendee"}):
        return redirect("route_after_login")

    event = get_object_or_404(Event, pk=event_id, status="approved")

    joined = Participation.objects.filter(user=request.user, event=event).exists()
    if not joined:
        messages.error(request, "Join the event first before giving feedback.")
        return redirect("events:attendee_events")

    existing = Feedback.objects.filter(event=event, user=request.user).first()

    if request.method == "POST":
        form = FeedbackForm(request.POST, instance=existing)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.event = event
            fb.user = request.user
            fb.save()
            messages.success(request, "Feedback saved successfully!")
            return redirect("events:attendee_events")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FeedbackForm(instance=existing)

    return render(request, "events/feedback_form.html", {
        "event": event,
        "form": form,
        "existing": existing,
    })


#This are for the organizer

@login_required
def organizer_dashboard(request):
    if not allow(request, {"organizer"}):
        return redirect("route_after_login")

    today = date.today()
    my_events = Event.objects.filter(organizer=request.user)

    total_events = my_events.count()
    pending = my_events.filter(status="pending").count()
    approved = my_events.filter(status="approved").count()
    declined = my_events.filter(status="declined").count()
    upcoming = my_events.filter(date__gte=today, status="approved").count()

    total_participants = Participation.objects.filter(event__organizer=request.user).count()
    total_feedback = Feedback.objects.filter(event__organizer=request.user).count()

    upcoming_list = my_events.filter(date__gte=today).order_by("date")[:5]

    return render(request, "events/organizer_dashboard.html", {
        "total_events": total_events,
        "pending": pending,
        "approved": approved,
        "declined": declined,
        "upcoming": upcoming,
        "total_participants": total_participants,
        "total_feedback": total_feedback,
        "upcoming_list": upcoming_list,
    })


@login_required
def organizer_events(request):
    if not allow(request, {"organizer"}):
        return redirect("route_after_login")

    # Read filters
    status = request.GET.get("status", "").strip()
    q = (request.GET.get("q") or "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to = request.GET.get("date_to", "").strip()

    # Base queryset
    my_events = Event.objects.filter(organizer=request.user)

    # Apply filters
    if status:
        my_events = my_events.filter(status=status)
    if q:
        my_events = my_events.filter(title__icontains=q)
    if date_from:
        my_events = my_events.filter(date__gte=date_from)
    if date_to:
        my_events = my_events.filter(date__lte=date_to)

    # Calculate feedback data (your existing logic)
    for e in my_events:
        feedbacks = Feedback.objects.filter(event=e)
        if feedbacks.exists():
            total = sum(f.rating for f in feedbacks)
            e.avg_rating = round(total / feedbacks.count(), 1)
            e.fb_count = feedbacks.count()
        else:
            e.avg_rating = "-"
            e.fb_count = 0

    # Render template with all filter values included
    return render(request, "events/organizer_events.html", {
        "my_events": my_events,
        "status": status,
        "q": q,
        "date_from": date_from,   # <-- IMPORTANT
        "date_to": date_to,       # <-- IMPORTANT
    })


@login_required
def event_create(request):
    if not allow(request, {"organizer"}):
        return redirect("route_after_login")

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)  # <-- add request.FILES here
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.status = "pending"
            event.save()
            
            max_participants = form.cleaned_data["max_participants"]
            EventCapacity.objects.create(event=event, max_participants=max_participants, current_participants=0)
            messages.success(request, "Event created and submitted for review.")
            return redirect("events:organizer_events")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EventForm()

    return render(request, "events/event_form.html", {"form": form})


@login_required
def event_update(request, pk):
    if not allow(request, {"organizer"}):
        return redirect("route_after_login")

    event = get_object_or_404(Event, pk=pk, organizer=request.user)

    if event.status in {"approved", "full"}:
        messages.warning(request, "Approved or full events can’t be edited.")
        return redirect("events:organizer_events")

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            updated_event = form.save()

            max_participants = form.cleaned_data["max_participants"]

            # make sure capacity exists, create if missing
            capacity, created = EventCapacity.objects.get_or_create(
                event=updated_event,
                defaults={
                    "max_participants": max_participants,
                    "current_participants": updated_event.participants.count(),
                },
            )
            # even if it already existed, update it
            capacity.max_participants = max_participants
            capacity.save()

            messages.success(request, "Event updated.")
            return redirect("events:organizer_events")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # ensure capacity exists for older events, with a sane default
        capacity, created = EventCapacity.objects.get_or_create(
            event=event,
            defaults={
                "max_participants": 1,
                "current_participants": event.participants.count(),
            },
        )

        form = EventForm(
            instance=event,
            initial={
                "max_participants": capacity.max_participants,
            },
        )

    return render(request, "events/event_form.html", {
        "form": form,
        "event": event,
    })


@login_required
def event_delete(request, pk):
    if not allow(request, {"organizer"}):
        return redirect("route_after_login")

    event = get_object_or_404(Event, pk=pk, organizer=request.user)
    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted.")
        return redirect("events:organizer_events")

    return render(request, "events/confirm_delete.html", {"object": event})


@login_required
def organizer_event_feedback(request, event_id):
    if not allow(request, {"organizer"}):
        return redirect("route_after_login")

    event = get_object_or_404(Event, pk=event_id, organizer=request.user)
    feedbacks = Feedback.objects.filter(event=event)

    if feedbacks.exists():
        total = sum(f.rating for f in feedbacks)
        avg = round(total / feedbacks.count(), 1)
    else:
        avg = "-"

    return render(request, "events/organizer_event_feedback.html", {
        "event": event,
        "feedbacks": feedbacks,
        "avg": avg,
    })


@login_required
def organizer_profile_edit(request):
    if not allow(request, {"organizer"}):
        return redirect("route_after_login")

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("events:organizer_profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "events/organizer_profile.html", {
        "form": form,
    })


#This are for the admin

@login_required
def admin_dashboard(request):
    if not (request.user.is_superuser or user_role(request.user) == "admin"):
        messages.error(request, "Admin access only.")
        return redirect("route_after_login")

    from datetime import timedelta
    today = date.today()
    week_from_now = today + timedelta(days=7)

    events_qs = Event.objects.all()

    total_events = events_qs.count()
    pending_events = events_qs.filter(status="pending").count()
    approved_events = events_qs.filter(status="approved").count()
    declined_events = events_qs.filter(status="declined").count()
    upcoming_events = events_qs.filter(date__gte=today).count()

    total_users = User.objects.count()
    attendees = User.objects.filter(profile__role="attendee").count()
    organizers = User.objects.filter(profile__role="organizer").count()
    admins = User.objects.filter(profile__role="admin").count()

    events_next_week = events_qs.filter(date__gte=today, date__lte=week_from_now).order_by("date")[:5]

    top_events = []
    approved = events_qs.filter(status="approved")
    for e in approved:
        fbs = Feedback.objects.filter(event=e)
        if fbs.exists():
            total = sum(f.rating for f in fbs)
            avg = round(total / fbs.count(), 1)
            top_events.append((avg, fbs.count(), e))
    top_events = sorted(top_events, key=lambda x: (-x[0], -x[1]))[:5]

    return render(request, "events/admin_dashboard.html", {
        "total_events": total_events,
        "pending_events": pending_events,
        "approved_events": approved_events,
        "declined_events": declined_events,
        "upcoming_events": upcoming_events,
        "total_users": total_users,
        "attendees": attendees,
        "organizers": organizers,
        "admins": admins,
        "events_next_week": events_next_week,
        "top_events": top_events,
    })


@login_required
def admin_review(request):
    if not (request.user.is_superuser or user_role(request.user) == "admin"):
        messages.error(request, "Admin access only.")
        return redirect("route_after_login")

    submissions = Event.objects.filter(status="pending")
    return render(request, "events/admin_events.html", {"submissions": submissions})


@login_required
def admin_approve(request, pk):
    if not (request.user.is_superuser or user_role(request.user) == "admin"):
        messages.error(request, "Admin access only.")
        return redirect("route_after_login")

    event = get_object_or_404(Event, pk=pk, status="pending")
    if request.method == "POST":
        event.status = "approved"
        event.save()
        messages.success(request, "Event approved.")
    return redirect("events:admin_review")


@login_required
def admin_decline(request, pk):
    if not (request.user.is_superuser or user_role(request.user) == "admin"):
        messages.error(request, "Admin access only.")
        return redirect("route_after_login")

    event = get_object_or_404(Event, pk=pk, status="pending")
    if request.method == "POST":
        event.status = "declined"
        event.save()
        messages.warning(request, "Event declined.")
    return redirect("events:admin_review")


@login_required
def admin_feedback_overview(request):
    """All events with filters + avg rating and review count."""
    if not (request.user.is_superuser or user_role(request.user) == "admin"):
        messages.error(request, "Admin access only.")
        return redirect("route_after_login")

    q = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()

    events = Event.objects.all()

    if q:
        events = events.filter(
            Q(title__icontains=q) |
            Q(organizer__username__icontains=q) |
            Q(organizer__first_name__icontains=q) |
            Q(organizer__last_name__icontains=q)
        )

    if status:
        events = events.filter(status=status)

    for e in events:
        feedbacks = Feedback.objects.filter(event=e)
        if feedbacks.exists():
            total = sum(f.rating for f in feedbacks)
            e.avg_rating = round(total / feedbacks.count(), 1)
            e.fb_count = feedbacks.count()
        else:
            e.avg_rating = "-"
            e.fb_count = 0

    return render(request, "events/admin_feedback_overview.html", {
        "events": events,
        "q": q,
        "status": status,
    })


@login_required
def admin_user_management(request):
    if not (request.user.is_superuser or user_role(request.user) == "admin"):
        messages.error(request, "Admin access only.")
        return redirect("route_after_login")

    role_filter = (request.GET.get("role") or "").strip()
    q = (request.GET.get("q") or "").strip()

    users = User.objects.all().select_related("profile").order_by("username")

    if role_filter:
        users = users.filter(profile__role=role_filter)

    if q:
        users = users.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )

    context = {
        "users": users,
        "role_filter": role_filter,
        "q": q,
    }
    return render(request, "events/admin_user_management.html", context)


#This part is for the shared parts

@login_required
def event_detail(request, event_id):
    """Detail page for an event, with participant list for organizers/admin."""
    event = get_object_or_404(Event, pk=event_id)
    joined = Participation.objects.filter(user=request.user, event=event).exists()

    participants = (
        Participation.objects
        .filter(event=event)
        .select_related("user")
        .order_by("joined_at")
    )

    return render(request, "events/event_detail.html", {
        "event": event,
        "joined": joined,
        "participants": participants,
    })
