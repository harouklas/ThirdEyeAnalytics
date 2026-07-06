from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories",
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "sub-categories"
        ordering = ["category__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["category", "slug"],
                name="unique_subcategory_slug_per_category",
            )
        ]

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Service(models.Model):
    class AnalysisType(models.TextChoices):
        TRACKING = "tracking", "Tracking"
        HEATMAP = "heatmap", "Heatmap"
        SCOUTING = "scouting", "Scouting"
        TACTICAL = "tactical", "Tactical"
        DETECTION = "detection", "Detection"
        PERFORMANCE = "performance", "Performance"
        HIGHLIGHT = "highlight", "Highlight"
        TEAM_SHAPE = "team_shape", "Team Shape"

    class SkillLevel(models.TextChoices):
        AMATEUR = "amateur", "Amateur"
        ACADEMY = "academy", "Academy"
        SEMI_PRO = "semi_pro", "Semi-Pro"
        PROFESSIONAL = "professional", "Professional"

    class VideoType(models.TextChoices):
        FULL_MATCH = "full_match", "Full Match"
        TRAINING = "training", "Training"
        PLAYER_CLIPS = "player_clips", "Player Clips"

    class DeliveryTime(models.TextChoices):
        HOURS_24 = "24h", "24 Hours"
        HOURS_48 = "48h", "48 Hours"
        DAYS_3_5 = "3_5_days", "3-5 Days"

    class OutputFormat(models.TextChoices):
        PDF_REPORT = "pdf_report", "PDF Report"
        DASHBOARD = "dashboard", "Dashboard"
        VIDEO_OVERLAY = "video_overlay", "Video Overlay"
        CSV_DATA = "csv_data", "CSV Data"

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="services",
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.PROTECT,
        related_name="services",
    )
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=170, unique=True)
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    analysis_type = models.CharField(max_length=30, choices=AnalysisType.choices)
    skill_level = models.CharField(max_length=30, choices=SkillLevel.choices)
    video_type = models.CharField(max_length=30, choices=VideoType.choices)
    delivery_time = models.CharField(max_length=30, choices=DeliveryTime.choices)
    output_format = models.CharField(max_length=30, choices=OutputFormat.choices)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="services/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category__name", "name"]

    def __str__(self):
        return self.name
