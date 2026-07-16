"""Automated tests for public catalogue behaviour."""

from django.test import TestCase
from django.urls import reverse

from .models import Category, Service, SubCategory


class CatalogueSearchSecurityTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Player Analysis", slug="player-analysis")
        subcategory = SubCategory.objects.create(
            category=category,
            name="Player Tracking",
            slug="player-tracking",
        )
        Service.objects.create(
            category=category,
            subcategory=subcategory,
            name="Safe Tracking Service",
            slug="safe-tracking-service",
            short_description="Tracks player movement.",
            description="A test service used to check catalogue searching.",
            analysis_type=Service.AnalysisType.TRACKING,
            skill_level=Service.SkillLevel.ACADEMY,
            video_type=Service.VideoType.PLAYER_CLIPS,
            delivery_time=Service.DeliveryTime.HOURS_48,
            output_format=Service.OutputFormat.PDF_REPORT,
            price="50.00",
        )

    def test_sql_looking_search_is_treated_as_plain_text(self):
        # Django ORM parameters keep this input as text instead of executable SQL.
        sql_looking_text = "' OR 1=1 --"
        response = self.client.get(
            reverse("catalogue:service_list"),
            {"q": sql_looking_text},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Safe Tracking Service")
        self.assertEqual(Service.objects.count(), 1)
