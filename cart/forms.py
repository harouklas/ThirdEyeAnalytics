"""Form for billing information used by the simulated checkout."""

import unicodedata

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


ALLOWED_UNICODE_JOINERS = {"\u200c", "\u200d"}


postal_code_validator = RegexValidator(
    regex=r"^[A-Za-z0-9]+(?:[ -][A-Za-z0-9]+)*$",
    message=(
        "Enter a valid postal code using letters and numbers, with single spaces "
        "or hyphens between groups."
    ),
)

vat_number_validator = RegexValidator(
    regex=r"^[A-Za-z0-9]+(?:[ .-][A-Za-z0-9]+)*$",
    message=(
        "Enter a valid VAT number using letters and numbers, with single spaces, "
        "periods, or hyphens between groups."
    ),
)


def _validate_characters(value, *, field_name, punctuation, allow_digits):
    """Keep billing text single-line while supporting international letters."""
    has_letter = any(character.isalpha() for character in value)
    has_digit = any(character.isdigit() for character in value)
    characters_are_valid = all(
        character.isalpha()
        or unicodedata.category(character).startswith("M")
        or character in ALLOWED_UNICODE_JOINERS
        or (allow_digits and character.isdigit())
        or character in punctuation
        for character in value
    )

    if not characters_are_valid or (not has_letter and not (allow_digits and has_digit)):
        digit_text = "letters, numbers," if allow_digits else "letters,"
        raise ValidationError(
            f"Enter a valid {field_name} using {digit_text} spaces, and common punctuation."
        )


def validate_full_name(value):
    _validate_characters(
        value,
        field_name="full name",
        punctuation=" .,'-’",
        allow_digits=False,
    )


def validate_organization(value):
    _validate_characters(
        value,
        field_name="organization",
        punctuation=" .,'-’&()+/",
        allow_digits=True,
    )


def validate_billing_address(value):
    _validate_characters(
        value,
        field_name="billing address",
        punctuation=" .,'-’#&()+/:;",
        allow_digits=True,
    )


def validate_city(value):
    _validate_characters(
        value,
        field_name="city",
        punctuation=" .,'-’",
        allow_digits=True,
    )


def validate_country(value):
    _validate_characters(
        value,
        field_name="country",
        punctuation=" .,'-’&()",
        allow_digits=False,
    )


def _normalize_single_line(value):
    """Normalize Unicode and collapse repeated whitespace before saving."""
    return " ".join(unicodedata.normalize("NFC", value).split())


class SingleLineCharField(forms.CharField):
    """Normalize Unicode and reject control characters before validation."""

    collapse_whitespace = False

    default_error_messages = {
        "single_line": "Enter a single-line value without control characters.",
    }

    def to_python(self, value):
        if value not in self.empty_values:
            value = unicodedata.normalize("NFC", str(value))
            if any(
                (
                    unicodedata.category(character).startswith("C")
                    and character not in ALLOWED_UNICODE_JOINERS
                )
                or unicodedata.category(character) in {"Zl", "Zp"}
                for character in value
            ):
                raise ValidationError(
                    self.error_messages["single_line"],
                    code="single_line",
                )

        value = super().to_python(value)
        if value and self.collapse_whitespace:
            return " ".join(value.split())
        return value


class NormalizedTextField(SingleLineCharField):
    """Collapse human-readable billing whitespace before other checks."""

    collapse_whitespace = True


class CheckoutForm(forms.Form):
    # Organization and VAT are optional; the remaining billing details are required.
    full_name = NormalizedTextField(
        min_length=2,
        max_length=150,
        label="Full name",
        validators=[validate_full_name],
        help_text="2-150 characters. Letters, spaces, apostrophes, periods, or hyphens.",
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    billing_email = forms.EmailField(
        max_length=254,
        label="Billing email",
        help_text="Enter a valid email address (maximum 254 characters).",
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    organization = NormalizedTextField(
        min_length=2,
        max_length=150,
        required=False,
        validators=[validate_organization],
        help_text="Optional. Use 2-150 characters if provided.",
        widget=forms.TextInput(attrs={"autocomplete": "organization"}),
    )
    billing_address = NormalizedTextField(
        min_length=5,
        max_length=255,
        label="Billing address",
        validators=[validate_billing_address],
        help_text="5-255 characters. Enter a single-line postal address.",
        widget=forms.TextInput(attrs={"autocomplete": "street-address"}),
    )
    city = NormalizedTextField(
        min_length=1,
        max_length=100,
        validators=[validate_city],
        help_text="1-100 characters. Letters, numbers, and common punctuation only.",
        widget=forms.TextInput(attrs={"autocomplete": "address-level2"}),
    )
    postal_code = SingleLineCharField(
        min_length=3,
        max_length=20,
        label="Postal code",
        validators=[postal_code_validator],
        help_text="3-20 characters. Letters, numbers, single spaces, and hyphens only.",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "postal-code",
                "pattern": r"[A-Za-z0-9]+(?:[ \-][A-Za-z0-9]+)*",
                "title": "Use letters and numbers with single spaces or hyphens between groups.",
            }
        ),
    )
    country = NormalizedTextField(
        min_length=2,
        max_length=100,
        initial="Greece",
        validators=[validate_country],
        help_text="2-100 characters. Letters and common punctuation only.",
        widget=forms.TextInput(attrs={"autocomplete": "country-name"}),
    )
    vat_number = SingleLineCharField(
        min_length=5,
        max_length=50,
        required=False,
        label="VAT number",
        validators=[vat_number_validator],
        help_text=(
            "Optional. Use 5-50 letters or numbers, with single spaces, periods, "
            "or hyphens between groups."
        ),
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "pattern": r"[A-Za-z0-9]+(?:[ .\-][A-Za-z0-9]+)*",
                "title": (
                    "Use letters and numbers with single spaces, periods, or hyphens "
                    "between groups."
                ),
            }
        ),
    )

    def clean_postal_code(self):
        return _normalize_single_line(self.cleaned_data["postal_code"]).upper()

    def clean_vat_number(self):
        return _normalize_single_line(self.cleaned_data["vat_number"]).upper()
