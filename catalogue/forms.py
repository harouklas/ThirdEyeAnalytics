"""Forms used by staff users to manage catalogue data."""

from decimal import Decimal

from django import forms
from django.utils.text import slugify

from .models import Category, Service, SubCategory


class LimitedImageField(forms.ImageField):
    """Reject large files before Pillow tries to decode their image content."""

    def to_python(self, data):
        if data and data.size > 5 * 1024 * 1024:
            raise forms.ValidationError("The image must be 5 MB or smaller.")

        image = super().to_python(data)
        if image:
            if image.image.format not in {"JPEG", "PNG", "WEBP"}:
                raise forms.ValidationError("Upload a JPEG, PNG, or WebP image.")
            if image.image.width > 5000 or image.image.height > 5000:
                raise forms.ValidationError("The image must be no larger than 5000 by 5000 pixels.")
        return image


class SlugFromNameMixin:
    def clean(self):
        # Create the URL part from the name when staff leave it blank.
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        slug = cleaned_data.get("slug")

        if name and not slug:
            cleaned_data["slug"] = slugify(name)

        return cleaned_data


class CategoryManagementForm(SlugFromNameMixin, forms.ModelForm):
    # Staff can type a slug or leave it blank for automatic generation.
    slug = forms.SlugField(required=False)
    description = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    class Meta:
        model = Category
        fields = ["name", "slug", "description"]


class SubCategoryManagementForm(SlugFromNameMixin, forms.ModelForm):
    # The selected category becomes the parent of the new sub-category.
    slug = forms.SlugField(required=False)
    description = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    class Meta:
        model = SubCategory
        fields = ["category", "name", "slug", "description"]

    def clean(self):
        cleaned_data = super().clean()
        selected_category = cleaned_data.get("category")

        # A service stores both category links, so moving a used sub-category
        # would make those two links disagree. Its name and text can still change.
        category_changed = (
            self.instance.pk
            and selected_category
            and self.instance.category_id != selected_category.id
        )
        if category_changed and self.instance.services.exists():
            self.add_error(
                "category",
                "This sub-category cannot move because one or more services use it.",
            )

        return cleaned_data


class ServiceManagementForm(SlugFromNameMixin, forms.ModelForm):
    # The mixin creates the slug if this is left blank.
    slug = forms.SlugField(required=False)
    description = forms.CharField(
        max_length=5000,
        widget=forms.Textarea(attrs={"rows": 5}),
    )
    price = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=Decimal("0.00"),
        max_value=Decimal("999999.99"),
    )
    image = LimitedImageField(required=False)

    class Meta:
        model = Service
        fields = [
            "category",
            "subcategory",
            "name",
            "slug",
            "short_description",
            "description",
            "analysis_type",
            "skill_level",
            "video_type",
            "delivery_time",
            "output_format",
            "price",
            "image",
            "is_active",
            "is_featured",
        ]

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        subcategory = cleaned_data.get("subcategory")

        if category and subcategory and subcategory.category_id != category.id:
            self.add_error("subcategory", "Select a sub-category from the chosen category.")

        return cleaned_data
