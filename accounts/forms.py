from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Profile

User = get_user_model()


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=150)
    phone_number = forms.CharField(max_length=30, required=False)
    organization = forms.CharField(max_length=150, required=False)
    sport_role = forms.ChoiceField(choices=Profile.SportRole.choices)
    favorite_analysis_type = forms.CharField(max_length=80, required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already used by another account.")
        return email


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = [
            "full_name",
            "email",
            "phone_number",
            "organization",
            "sport_role",
            "favorite_analysis_type",
            "bio",
        ]

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if user:
            self.fields["email"].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            if self.user:
                self.user.email = self.cleaned_data["email"]
                self.user.save(update_fields=["email"])
        return profile
