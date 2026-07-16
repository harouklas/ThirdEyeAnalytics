"""Tests that public Viewers cannot use ratings or wishlists."""

from django.test import TestCase
from django.urls import reverse

class PublicViewerInteractionPermissionTests(TestCase):
    # Anonymous visitors should be sent to login before either action runs.
    def test_public_viewer_cannot_rate_a_service(self):
        rating_url = reverse("interactions:rate_service", args=[999])
        response = self.client.post(
            rating_url,
            {"score": 5},
        )

        login_url = reverse("accounts:login")
        self.assertRedirects(response, f"{login_url}?next={rating_url}")

    def test_public_viewer_cannot_use_wishlist(self):
        wishlist_url = reverse("interactions:toggle_wishlist", args=[999])
        response = self.client.post(wishlist_url)

        login_url = reverse("accounts:login")
        self.assertRedirects(response, f"{login_url}?next={wishlist_url}")
