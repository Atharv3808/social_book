from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


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
