from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    # Attendee
    path("attendee/events/", views.attendee_events, name="attendee_events"),  # All events
    path("attendee/my-events/", views.attendee_my_events, name="attendee_my_events"),  # My registered events
    path("attendee/events/<int:event_id>/join/", views.attendee_join_event, name="attendee_join_event"),
    path("attendee/events/<int:event_id>/leave/", views.attendee_leave_event, name="attendee_leave_event"),
    path("attendee/events/<int:event_id>/feedback/", views.feedback_create, name="feedback_create"),
    path("attendee/profile/", views.attendee_profile_edit, name="attendee_profile"),

    # Organizer
    path("organizer/dashboard/", views.organizer_dashboard, name="organizer_dashboard"),
    path("organizer/events/", views.organizer_events, name="organizer_events"),
    path("organizer/events/create/", views.event_create, name="event_create"),
    path("organizer/events/<int:pk>/update/", views.event_update, name="event_update"),
    path("organizer/events/<int:pk>/delete/", views.event_delete, name="event_delete"),
    path("organizer/events/<int:event_id>/feedback/", views.organizer_event_feedback, name="organizer_event_feedback"),
    path("organizer/profile/", views.organizer_profile_edit, name="organizer_profile"),

    # Admin
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/review/", views.admin_review, name="admin_review"),
    path("admin/events/", views.admin_review, name="admin_events"),  # alias to review list
    path("admin/approve/<int:pk>/", views.admin_approve, name="admin_approve"),
    path("admin/decline/<int:pk>/", views.admin_decline, name="admin_decline"),
    path("admin/feedback/", views.admin_feedback_overview, name="admin_feedback_overview"),  # All events
    path("admin/users/", views.admin_user_management, name="admin_user_management"),

    # Event detail page (shared)
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
]
