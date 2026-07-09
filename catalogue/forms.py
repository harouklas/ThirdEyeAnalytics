from django import forms
from django.utils.text import slugify

from .models import Category, Service, SubCategory


class SlugFromNameMixin:
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        slug = cleaned_data.get("slug")

        if name and not slug:
            cleaned_data["slug"] = slugify(name)

        return cleaned_data


class CategoryManagementForm(SlugFromNameMixin, forms.ModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model = Category
        fields = ["name", "slug", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class SubCategoryManagementForm(SlugFromNameMixin, forms.ModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model = SubCategory
        fields = ["category", "name", "slug", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ServiceManagementForm(SlugFromNameMixin, forms.ModelForm):
    slug = forms.SlugField(required=False)

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
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }
