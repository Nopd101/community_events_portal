from django import forms
from .models import Event, Feedback, EventCapacity


class EventForm(forms.ModelForm):
    max_participants = forms.IntegerField(
        min_value=1,
        label="Maximum Participants",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
        }),
    )
    class Meta:
        model = Event
        fields = ["image", "title", "short_description", "date","start_time", "end_time", "location","max_participants" ]
        widgets = {
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
            "title": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control",
            }),
            "start_time": forms.TimeInput(attrs={
                "type": "time",
                "class": "form-control",
            }),
            "end_time": forms.TimeInput(attrs={
                "type": "time",
                "class": "form-control",
            }),
            "location": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "short_description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
            }),
            "max_participants": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
            }),
        }
        labels = {
            "title": "Title",
            "date": "Date",
            "start_time": "Start time",
            "end_time": "End time",
            "location": "Location",
            "short_description": "Short description",
            "image": "Event image",
            "max_participants": "Maximum Participants",
        }



class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 5,
            }),
            "comment": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
        }
        labels = {
            "rating": "Rating (1–5)",
            "comment": "Comment (optional)",
        }
        
class EventCapacityForm(forms.ModelForm):
    class Meta:
        model = EventCapacity
        fields = ["max_participants"]
        widgets = {
            "max_participants": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }
