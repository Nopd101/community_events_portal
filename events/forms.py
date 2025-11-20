from django import forms
from .models import Event, Feedback


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "date", "location", "short_description"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "date": forms.DateInput(attrs={
                "type": "date",          # <--- browser date picker
                "class": "form-control",
            }),
            "location": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "short_description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
            }),
        }
        labels = {
            "title": "Title",
            "date": "Date",
            "location": "Location",
            "short_description": "Short description",
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