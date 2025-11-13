from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model
from django.db.models import Q


def _apply_bootstrap_attrs(form):
    """Apply Bootstrap classes to form widgets.

    - Use form-control for standard inputs
    - Use form-check-input for checkboxes
    """
    for name, field in form.fields.items():
        widget = field.widget
        attrs = widget.attrs
        existing = attrs.get("class", "")
        input_type = getattr(widget, "input_type", "")
        if input_type == "checkbox":
            classes = (existing + " form-check-input").strip()
        else:
            classes = (existing + " form-control").strip()
        attrs["class"] = classes
        # set placeholder for text-like inputs only
        if input_type in {"text", "email", "password", "number"} and "placeholder" not in attrs:
            attrs["placeholder"] = field.label


def register(request):
    """Register a new user. On success, log the user in and redirect to home.

    Uses Django's built-in UserCreationForm for simplicity.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        _apply_bootstrap_attrs(form)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. You are now logged in.")
            return redirect("home")
    else:
        form = CustomUserCreationForm()
        _apply_bootstrap_attrs(form)
    return render(request, "accounts/register.html", {"form": form})


def logout_view(request):
    """Log the user out and redirect to home. Accepts GET for convenience in the navbar link."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


class ThemedLoginView(LoginView):
    """LoginView that applies Bootstrap classes to form widgets."""
    template_name = "registration/login.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        _apply_bootstrap_attrs(form)
        return form


def authors_sellers(request):
    """List users who opted into public visibility.

    Supports simple search via query parameter `q` across username, first_name, last_name, and email.
    """
    User = get_user_model()
    qs = User.objects.filter(public_visibility=True)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(username__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(email__icontains=q)
        )
    qs = qs.order_by("-date_joined")
    return render(request, "accounts/authors_sellers.html", {"users": qs, "q": q})
