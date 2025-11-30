from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import UploadedFile
from .forms import UploadedFileForm, TwoStepLoginForm, TwoStepCodeForm
from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import FileResponse
import mimetypes
from django.conf import settings
from django.utils import timezone
import random
import string
import logging

logger = logging.getLogger(__name__)


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


@login_required
def upload_books_dashboard(request):
    """Upload Books dashboard: upload a new file and list user's uploads."""
    if request.method == "POST":
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "File uploaded successfully.")
            return redirect("accounts:upload_books")
    else:
        form = UploadedFileForm()

    # Apply bootstrap styles similar to other forms
    _apply_bootstrap_attrs(form)

    uploads = UploadedFile.objects.filter(user=request.user)
    return render(request, "accounts/upload_books.html", {"form": form, "uploads": uploads})


def require_user_has_uploads(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        has_uploads = UploadedFile.objects.filter(user=request.user).exists()
        if not has_uploads:
            return HttpResponseRedirect(reverse("accounts:upload_books"))
        return view_func(request, *args, **kwargs)
    return _wrapped


@login_required
@require_user_has_uploads
def my_books_dashboard(request):
    uploads = UploadedFile.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "accounts/my_books.html", {"uploads": uploads})


@login_required
def download_my_book(request, pk):
    obj = get_object_or_404(UploadedFile, pk=pk)
    # Allow owner; optionally allow public visibility files
    if obj.user != request.user and obj.visibility != "public":
        return HttpResponseRedirect(reverse("accounts:my_books"))

    if not obj.file:
        return HttpResponseRedirect(reverse("accounts:my_books"))

    file_handle = obj.file.open("rb")
    content_type, _ = mimetypes.guess_type(obj.file.name)
    response = FileResponse(file_handle, content_type=content_type or "application/octet-stream")
    response["Content-Disposition"] = f"attachment; filename={obj.file.name.split('/')[-1]}"
    return response


def two_step_login(request):
    """Step 1: Accept username/password, authenticate, generate OTP, and redirect to verify."""
    if request.method == "POST":
        form = TwoStepLoginForm(request.POST)
        _apply_bootstrap_attrs(form)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is None or not getattr(user, "is_active", True):
                messages.error(request, "Invalid credentials or inactive account.")
            else:
                # Require an email address to deliver the verification code
                email = getattr(user, "email", None)
                if not email:
                    messages.error(
                        request,
                        "No email is associated with this account. Please add an email to receive the verification code.",
                    )
                else:
                    # generate 6-digit code and store in session with expiry (5 minutes)
                    code = "".join(random.choices(string.digits, k=6))
                    request.session["two_step_user_id"] = user.id
                    request.session["two_step_code"] = code
                    request.session["two_step_expires_at"] = (timezone.now() + timezone.timedelta(minutes=5)).isoformat()

                    # Send the code via email
                    from django.core.mail import send_mail
                    try:
                        send_mail(
                            subject="Your verification code",
                            message=f"Your verification code is: {code}",
                            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                            recipient_list=[email],
                            fail_silently=False,
                        )
                        messages.info(request, "Verification code sent to your email.")
                        return redirect("accounts:login_two_step_verify")
                    except Exception as e:
                        logger.exception("Failed to send verification email for user '%s'", username)
                        if getattr(settings, "DEBUG", False):
                            messages.warning(
                                request,
                                "Email delivery failed in development; proceeding to verification page.",
                            )
                            return redirect("accounts:login_two_step_verify")
                        messages.error(request, "Could not send verification email. Please try again later.")
    else:
        form = TwoStepLoginForm()
        _apply_bootstrap_attrs(form)
    return render(request, "accounts/two_step_login.html", {"form": form})


def two_step_verify(request):
    """Step 2: Verify the code and complete login."""
    user_id = request.session.get("two_step_user_id")
    session_code = request.session.get("two_step_code")
    expires_at = request.session.get("two_step_expires_at")

    if not user_id or not session_code or not expires_at:
        messages.error(request, "Verification session expired or not started.")
        return redirect("accounts:login_two_step")

    # Expiry check
    try:
        expires_dt = timezone.datetime.fromisoformat(expires_at)
        if timezone.is_naive(expires_dt):
            expires_dt = timezone.make_aware(expires_dt)
    except Exception:
        expires_dt = timezone.now()
    if timezone.now() > expires_dt:
        for k in ("two_step_user_id", "two_step_code", "two_step_expires_at"):
            request.session.pop(k, None)
        messages.error(request, "Verification code expired. Please log in again.")
        return redirect("accounts:login_two_step")

    if request.method == "POST":
        form = TwoStepCodeForm(request.POST)
        _apply_bootstrap_attrs(form)
        if form.is_valid():
            code = form.cleaned_data["code"].strip()
            if code == session_code:
                User = get_user_model()
                try:
                    user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    user = None
                for k in ("two_step_user_id", "two_step_code", "two_step_expires_at"):
                    request.session.pop(k, None)
                if user:
                    # Send login notification to a specific recipient if configured
                    notify_recipient = getattr(settings, "LOGIN_NOTIFICATION_RECIPIENT", None)
                    if notify_recipient:
                        from django.core.mail import send_mail
                        try:
                            send_mail(
                                subject="User Login Notification",
                                message=(
                                    f"User '{user.username}' logged in successfully at "
                                    f"{timezone.now().strftime('%Y-%m-%d %H:%M:%S %Z')}"
                                ),
                                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                                recipient_list=[notify_recipient],
                                fail_silently=True,
                            )
                        except Exception:
                            # Silently ignore notification failures to not block login
                            pass
                    login(request, user)
                    messages.success(request, "Login successful.")
                    return redirect("home")
                else:
                    messages.error(request, "User not found.")
            else:
                messages.error(request, "Invalid verification code.")
    else:
        form = TwoStepCodeForm()
        _apply_bootstrap_attrs(form)

    # In development, you may want to show the code for testing
    dev_hint = None
    if getattr(settings, "DEBUG", False):
        dev_hint = session_code

    return render(request, "accounts/two_step_verify.html", {"form": form, "dev_code": dev_hint})
