from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import UploadedFile
from django.utils import timezone


class CustomUserCreationForm(UserCreationForm):
    """User creation form bound to the custom user model.

    Includes profile fields so they can be set during registration.
    Password fields are provided by UserCreationForm.
    """

    class Meta:
        model = get_user_model()
        # Model fields available at registration; password1/password2 are added by UserCreationForm
        fields = (
            "username",
            "email",
            "public_visibility",
            "birth_year",
            "address",
        )

    def clean_birth_year(self):
        birth_year = self.cleaned_data.get("birth_year")
        if birth_year is None:
            return birth_year
        # simple sanity bounds; adjust as needed
        if birth_year < 1900:
            raise forms.ValidationError("Birth year must be >= 1900")
        return birth_year


class UploadedFileForm(forms.ModelForm):
    """Form for uploading books/files with metadata.

    Restrict file types on the client via `accept` and validate on the server.
    """

    class Meta:
        model = UploadedFile
        fields = [
            "title",
            "description",
            "visibility",
            "cost",
            "year_published",
            "file",
        ]
        widgets = {
            # Restrict accepted MIME types to PDF and JPEG on the client side
            "file": forms.ClearableFileInput(attrs={"accept": "application/pdf,image/jpeg"}),
            "title": forms.TextInput(attrs={
                "placeholder": "Title of book or file",
            }),
            "description": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Short description (optional)",
            }),
            "cost": forms.NumberInput(attrs={
                "min": "0",
                "step": "0.01",
                "placeholder": "0.00",
            }),
            "year_published": forms.NumberInput(attrs={
                "min": "1500",
                "max": str(timezone.now().year),
                "placeholder": "e.g., 2021",
            }),
        }

        help_texts = {
            "visibility": "Choose whether the file is visible publicly or private to you.",
            "cost": "Enter a non-negative amount (two decimal places).",
            "year_published": "Enter a year between 1500 and the current year.",
        }

    def clean_file(self):
        f = self.cleaned_data.get("file")
        if not f:
            return f
        content_type = getattr(f, "content_type", None)
        allowed = {"application/pdf", "image/jpeg"}
        if content_type not in allowed:
            raise forms.ValidationError("Only PDF and JPEG files are allowed.")
        return f

    def clean_year_published(self):
        y = self.cleaned_data.get("year_published")
        if y is None:
            return y
        if y < 1500:
            raise forms.ValidationError("Please enter a reasonable publication year (>= 1500).")
        current_year = timezone.now().year
        if y > current_year:
            raise forms.ValidationError(f"Publication year cannot be in the future (<= {current_year}).")
        return y

    def clean_cost(self):
        c = self.cleaned_data.get("cost")
        if c is None:
            return c
        if c < 0:
            raise forms.ValidationError("Cost must be a non-negative amount.")
        return c


class TwoStepLoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class TwoStepCodeForm(forms.Form):
    code = forms.CharField(label="Verification Code", max_length=6)
