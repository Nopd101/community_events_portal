from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [("organizer", "Organizer"), ("attendee", "Attendee")]

    first_name = forms.CharField(max_length=150, required=True)
    last_name  = forms.CharField(max_length=150, required=True)
    email      = forms.EmailField(required=True)
    role       = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model  = User
        fields = ("username", "first_name", "last_name", "email", "role", "password1", "password2")

    def clean_email(self):
        return self.cleaned_data["email"].lower()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name  = self.cleaned_data["last_name"]
        user.email      = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    
User = get_user_model()

ROLE_CHOICES = [
    ("attendee", "Attendee"),
    ("organizer", "Organizer"),
    ("admin", "Admin"),
]

class AdminUserForm(forms.ModelForm):
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active"]

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email address",
        }