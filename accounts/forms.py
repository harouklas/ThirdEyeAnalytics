"""Forms for user registration and profile editing."""

import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator

from .models import Profile, phone_number_validator

User = get_user_model()

username_validator = RegexValidator(
    regex=r"^[A-Za-z0-9._]*[A-Za-z0-9]$",
    message="Use only letters, numbers, dots, or underscores, and end with a letter or number.",
)


def validate_name(value):
    # isalpha also accepts Greek and accented letters, but rejects numbers and symbols.
    if not value.isalpha():
        raise forms.ValidationError("Use letters only, without numbers or symbols.")


class RegistrationForm(UserCreationForm):
    # Extend Django's account form instead of handling passwords ourselves.
    username = forms.CharField(
        max_length=10,
        validators=[username_validator],
        help_text="Maximum 10 characters. Only letters, numbers, dots, and underscores.",
    )
    email = forms.EmailField(max_length=254, required=True)
    password1 = forms.CharField(
        label="Password",
        min_length=8,
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="At least 8 characters with a lowercase letter, capital letter, number, and symbol.",
    )
    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    first_name = forms.CharField(
        label="Name",
        max_length=50,
        validators=[validate_name],
    )
    last_name = forms.CharField(
        label="Surname",
        max_length=50,
        validators=[validate_name],
    )
    phone_country_code = forms.ChoiceField(
        label="Phone country",
        choices=Profile.PhoneCountry.choices,
        initial=Profile.PhoneCountry.GREECE,
    )
    phone_number = forms.CharField(
        min_length=6,
        max_length=15,
        validators=[phone_number_validator],
        help_text="Numbers only, without spaces or symbols.",
    )
    organization = forms.CharField(max_length=25, required=False)
    sport_role = forms.ChoiceField(choices=Profile.SportRole.choices)
    favorite_analysis_type = forms.CharField(max_length=80, required=False)
    bio = forms.CharField(
        max_length=250,
        widget=forms.Textarea(attrs={"rows": 4}),
        required=False,
    )

    field_order = [
        "username",
        "email",
        "password1",
        "password2",
        "first_name",
        "last_name",
        "phone_country_code",
        "phone_number",
        "organization",
        "sport_role",
        "favorite_analysis_type",
        "bio",
    ]

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        # Do not allow two accounts to register with the same email address.
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already used by another account.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password1")
        username = cleaned_data.get("username", "")
        email = cleaned_data.get("email", "")

        if not password:
            return cleaned_data

        # Add separate errors so the user can see exactly which rule failed.
        if not re.search(r"[a-z]", password):
            self.add_error("password1", "Password must contain a lowercase letter.")
        if not re.search(r"[A-Z]", password):
            self.add_error("password1", "Password must contain a capital letter.")
        if not re.search(r"[0-9]", password):
            self.add_error("password1", "Password must contain a number.")
        if not re.search(r"[^A-Za-z0-9\s]", password):
            self.add_error("password1", "Password must contain a symbol.")
        if any(character.isspace() for character in password):
            self.add_error("password1", "Password cannot contain spaces.")
        if username and password.casefold() == username.casefold():
            self.add_error("password1", "Password cannot be the same as your username.")
        if email and password.casefold() == email.casefold():
            self.add_error("password1", "Password cannot be the same as your email.")

        return cleaned_data


class ProfileForm(forms.ModelForm):
    # Name and email are stored on Django User while the remaining fields belong to Profile.
    first_name = forms.CharField(
        label="Name",
        max_length=50,
        validators=[validate_name],
    )
    last_name = forms.CharField(
        label="Surname",
        max_length=50,
        validators=[validate_name],
    )
    email = forms.EmailField(max_length=254, required=True)
    phone_country_code = forms.ChoiceField(
        label="Phone country",
        choices=Profile.PhoneCountry.choices,
    )
    phone_number = forms.CharField(
        min_length=6,
        max_length=15,
        validators=[phone_number_validator],
        help_text="Numbers only, without spaces or symbols.",
    )
    organization = forms.CharField(max_length=25, required=False)
    bio = forms.CharField(
        max_length=250,
        widget=forms.Textarea(attrs={"rows": 4}),
        required=False,
    )

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_country_code",
            "phone_number",
            "organization",
            "sport_role",
            "favorite_analysis_type",
            "bio",
        ]

    def __init__(self, *args, user=None, **kwargs):
        # Older profiles may only have full_name, so use it as a fallback.
        self.user = user
        super().__init__(*args, **kwargs)
        if user:
            stored_first_name, _separator, stored_last_name = self.instance.full_name.partition(" ")
            self.fields["email"].initial = user.email
            self.fields["first_name"].initial = user.first_name or stored_first_name
            self.fields["last_name"].initial = user.last_name or stored_last_name

    def save(self, commit=True):
        # User owns login details while Profile keeps the combined display name.
        profile = super().save(commit=False)
        profile.full_name = f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}"
        if commit:
            profile.save()
            if self.user:
                self.user.email = self.cleaned_data["email"]
                self.user.first_name = self.cleaned_data["first_name"]
                self.user.last_name = self.cleaned_data["last_name"]
                self.user.save(update_fields=["email", "first_name", "last_name"])
        return profile

    def clean_email(self):
        # Exclude this user's current account while checking for duplicate emails.
        email = self.cleaned_data["email"]
        existing_users = User.objects.filter(email__iexact=email)
        if self.user:
            existing_users = existing_users.exclude(id=self.user.id)
        if existing_users.exists():
            raise forms.ValidationError("This email is already used by another account.")
        return email
