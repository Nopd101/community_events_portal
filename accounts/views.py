from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from django.db import transaction
from .forms import CustomUserCreationForm
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import AdminUserForm

#def login_user(request):
    #if request.method == "POST":
        #username = request.POST["username"]
        #password = request.POST["password"]
        #user = authenticate(request, username=username, password=password)
        #if user is not None:
            #login(request, user)
        #else:
            #messages.success(request, ("There was an error logging in, Try again..."))
            #return redirect('login')
    #return render(request, 'registration/login.html', {})

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                role = form.cleaned_data["role"]
                Profile.objects.create(user=user, role=role)

                group_name = "Organizer" if role == "organizer" else "Attendee"
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)

            login(request, user)
            messages.success(request, "Welcome! Your account was created.")
            return redirect("accounts:route_after_login")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def route_after_login(request):
    user = request.user
    role = user.profile.role 
    
    if user.is_superuser or role == "admin":
        return redirect(reverse("events:admin_dashboard"))
    elif role == "organizer":
        return redirect(reverse("events:organizer_dashboard"))
    else:
        return redirect(reverse("events:attendee_events"))
    
def logout_user(request):
    logout(request)
    return redirect(login)

User = get_user_model()


def _is_admin(user):
    """Helper: return True if user is superuser or has profile.role == 'admin'."""
    if user.is_superuser:
        return True
    profile = getattr(user, "profile", None)
    return bool(profile and profile.role == "admin")


@login_required
def admin_user_edit(request, pk):
    if not _is_admin(request.user):
        messages.error(request, "Admin access only.")
        return redirect("events:admin_user_management")

    user_obj = get_object_or_404(User, pk=pk)
    profile, _ = Profile.objects.get_or_create(user=user_obj)

    if request.method == "POST":
        form = AdminUserForm(request.POST, instance=user_obj)
        if form.is_valid():
            user_obj = form.save()
            profile.role = form.cleaned_data["role"]
            profile.save()
            messages.success(request, "User updated successfully.")
            return redirect("events:admin_user_management")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AdminUserForm(instance=user_obj, initial={"role": profile.role})

    return render(request, "accounts/admin_user_edit.html", {
        "form": form,
        "user_obj": user_obj,
    })


@login_required
def admin_user_delete(request, pk):
    if not _is_admin(request.user):
        messages.error(request, "Admin access only.")
        return redirect("events:admin_user_management")

    user_obj = get_object_or_404(User, pk=pk)

    if user_obj == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("events:admin_user_management")

    if request.method == "POST":
        user_obj.delete()
        messages.success(request, "User deleted successfully.")
        return redirect("events:admin_user_management")

    return render(request, "accounts/admin_user_delete.html", {
        "user_obj": user_obj,
    })