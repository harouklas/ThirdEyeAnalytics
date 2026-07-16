"""Security regression tests for the main ThirdEye user flows."""

from io import BytesIO

from PIL import Image

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.html import escape

from accounts.forms import ProfileForm, RegistrationForm
from accounts.models import Profile
from cart.forms import CheckoutForm
from cart.models import Cart, CartItem, Order
from catalogue.forms import ServiceManagementForm
from catalogue.models import Category, Service, SubCategory
from interactions.models import Rating, SearchHistory

User = get_user_model()


class ThirdEyeSecurityTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Player Analysis",
            slug="player-analysis",
        )
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            name="Player Tracking",
            slug="player-tracking",
        )
        self.other_category = Category.objects.create(
            name="Match Analysis",
            slug="match-analysis",
        )
        self.other_subcategory = SubCategory.objects.create(
            category=self.other_category,
            name="Tactical Reports",
            slug="tactical-reports",
        )
        self.service = Service.objects.create(
            category=self.category,
            subcategory=self.subcategory,
            name="Player Tracking Package",
            slug="player-tracking-package",
            short_description="Tracks player movement.",
            description="A player tracking service used by the security tests.",
            analysis_type=Service.AnalysisType.TRACKING,
            skill_level=Service.SkillLevel.ACADEMY,
            video_type=Service.VideoType.PLAYER_CLIPS,
            delivery_time=Service.DeliveryTime.HOURS_48,
            output_format=Service.OutputFormat.PDF_REPORT,
            price="79.00",
        )
        self.user = User.objects.create_user(
            username="security-user",
            email="security@example.com",
            password="StrongTestPassword!4826",
        )
        self.profile = Profile.objects.create(
            user=self.user,
            full_name="Security User",
            sport_role=Profile.SportRole.ANALYST,
        )
        self.other_user = User.objects.create_user(
            username="other-user",
            email="other@example.com",
            password="StrongTestPassword!5937",
        )
        Profile.objects.create(
            user=self.other_user,
            full_name="Other User",
            sport_role=Profile.SportRole.COACH,
        )

    def valid_registration_data(self):
        return {
            "username": "secure.1",
            "email": "new-security@example.com",
            "password1": "StrongRegistrationPassword!6842",
            "password2": "StrongRegistrationPassword!6842",
            "first_name": "Security",
            "last_name": "User",
            "phone_country_code": Profile.PhoneCountry.GREECE,
            "phone_number": "2101234567",
            "organization": "Test Academy",
            "sport_role": Profile.SportRole.ANALYST,
            "favorite_analysis_type": "Tracking",
            "bio": "A valid profile biography.",
        }

    def valid_service_data(self):
        return {
            "category": self.category.id,
            "subcategory": self.subcategory.id,
            "name": "Secure Analysis Service",
            "slug": "secure-analysis-service",
            "short_description": "A safely validated service.",
            "description": "A normal catalogue description.",
            "analysis_type": Service.AnalysisType.TRACKING,
            "skill_level": Service.SkillLevel.ACADEMY,
            "video_type": Service.VideoType.PLAYER_CLIPS,
            "delivery_time": Service.DeliveryTime.HOURS_48,
            "output_format": Service.OutputFormat.PDF_REPORT,
            "price": "100.00",
            "is_active": True,
            "is_featured": False,
        }

    def test_reflected_xss_search_text_is_escaped(self):
        payload = '<script>alert("search-xss")</script>'
        response = self.client.get(reverse("catalogue:service_list"), {"q": payload})

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, payload)
        self.assertContains(response, escape(payload))

    def test_stored_xss_profile_name_is_escaped(self):
        payload = '<img src=x onerror=alert("profile-xss")>'
        self.profile.full_name = payload
        self.profile.save(update_fields=["full_name"])
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertNotContains(response, payload)
        self.assertContains(response, escape(payload))

    def test_stored_xss_service_name_is_escaped(self):
        payload = '<svg onload=alert("service-xss")>'
        self.service.name = payload
        self.service.save(update_fields=["name"])

        response = self.client.get(reverse("catalogue:service_list"))

        self.assertNotContains(response, payload)
        self.assertContains(response, escape(payload))

    def test_long_search_is_limited_before_history_is_saved(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("catalogue:service_list"), {"q": "x" * 5000})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(SearchHistory.objects.get(user=self.user).query), 150)

    def test_invalid_filter_choice_is_ignored(self):
        response = self.client.get(
            reverse("catalogue:service_list"),
            {"analysis_type": "tracking' OR 1=1 --"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["filters"]["analysis_type"], "")

    def test_registration_rejects_long_and_badly_formatted_input(self):
        data = self.valid_registration_data()
        data["first_name"] = "Name2"
        data["last_name"] = "Surname!"
        data["phone_number"] = "not-a-phone<script>"
        data["organization"] = "o" * 26
        data["bio"] = "b" * 251

        form = RegistrationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertIn("last_name", form.errors)
        self.assertIn("phone_number", form.errors)
        self.assertIn("organization", form.errors)
        self.assertIn("bio", form.errors)

    def test_registration_cannot_assign_an_administrator_role(self):
        data = self.valid_registration_data()
        data["role"] = Profile.UserRole.HEAD_ADMINISTRATOR

        response = self.client.post(reverse("accounts:register"), data)

        self.assertEqual(response.status_code, 302)
        created_user = User.objects.get(username=data["username"])
        self.assertEqual(created_user.profile.role, Profile.UserRole.USER)
        self.assertFalse(created_user.is_staff)
        self.assertFalse(created_user.is_superuser)

    def test_profile_edit_rejects_another_users_email(self):
        form = ProfileForm(
            data={
                "first_name": "Security",
                "last_name": "User",
                "email": self.other_user.email.upper(),
                "phone_country_code": Profile.PhoneCountry.GREECE,
                "phone_number": "2101234567",
                "organization": "Test Academy",
                "sport_role": Profile.SportRole.ANALYST,
                "favorite_analysis_type": "Tracking",
                "bio": "Valid biography.",
            },
            instance=self.profile,
            user=self.user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_checkout_rejects_wrong_email_postal_and_vat_formats(self):
        form = CheckoutForm(
            data={
                "full_name": "Security User",
                "billing_email": "not-an-email",
                "organization": "Test Academy",
                "billing_address": "1 Test Street",
                "city": "Athens",
                "postal_code": "<script>",
                "country": "Greece",
                "vat_number": "!@#",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("billing_email", form.errors)
        self.assertIn("postal_code", form.errors)
        self.assertIn("vat_number", form.errors)

    def test_service_form_rejects_negative_price_and_wrong_subcategory(self):
        data = self.valid_service_data()
        data["price"] = "-1.00"
        data["subcategory"] = self.other_subcategory.id

        form = ServiceManagementForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)
        self.assertIn("subcategory", form.errors)

    def test_service_form_rejects_oversized_image(self):
        image_buffer = BytesIO()
        Image.new("RGB", (20, 20), "red").save(image_buffer, format="PNG")
        oversized_content = image_buffer.getvalue() + (b"0" * (5 * 1024 * 1024))
        oversized_image = SimpleUploadedFile(
            "oversized.png",
            oversized_content,
            content_type="image/png",
        )

        form = ServiceManagementForm(
            data=self.valid_service_data(),
            files={"image": oversized_image},
        )

        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)
        self.assertIn("5 MB", form.errors["image"][0])

    def test_non_image_upload_is_rejected(self):
        fake_image = SimpleUploadedFile(
            "malicious.jpg",
            b"this is not an image",
            content_type="image/jpeg",
        )

        form = ServiceManagementForm(
            data=self.valid_service_data(),
            files={"image": fake_image},
        )

        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)

    def test_unsupported_image_format_is_rejected(self):
        image_buffer = BytesIO()
        Image.new("RGB", (20, 20), "blue").save(image_buffer, format="GIF")
        gif_image = SimpleUploadedFile(
            "unsupported.gif",
            image_buffer.getvalue(),
            content_type="image/gif",
        )

        form = ServiceManagementForm(
            data=self.valid_service_data(),
            files={"image": gif_image},
        )

        self.assertFalse(form.is_valid())
        self.assertIn("JPEG, PNG, or WebP", form.errors["image"][0])

    def test_image_with_extreme_dimensions_is_rejected(self):
        image_buffer = BytesIO()
        Image.new("RGB", (5001, 1), "green").save(image_buffer, format="PNG")
        wide_image = SimpleUploadedFile(
            "too-wide.png",
            image_buffer.getvalue(),
            content_type="image/png",
        )

        form = ServiceManagementForm(
            data=self.valid_service_data(),
            files={"image": wide_image},
        )

        self.assertFalse(form.is_valid())
        self.assertIn("5000 by 5000", form.errors["image"][0])

    def test_image_renamed_with_an_html_extension_is_rejected(self):
        image_buffer = BytesIO()
        Image.new("RGB", (20, 20), "yellow").save(image_buffer, format="PNG")
        renamed_image = SimpleUploadedFile(
            "renamed-image.html",
            image_buffer.getvalue(),
            content_type="image/png",
        )

        form = ServiceManagementForm(
            data=self.valid_service_data(),
            files={"image": renamed_image},
        )

        self.assertFalse(form.is_valid())
        self.assertIn("extension", form.errors["image"][0].lower())

    def test_service_form_rejects_excessively_long_description(self):
        data = self.valid_service_data()
        data["description"] = "d" * 5001

        form = ServiceManagementForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)

    def test_post_actions_reject_missing_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)

        response = csrf_client.post(
            reverse("interactions:rate_service", args=[self.service.id]),
            {"score": 5},
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Rating.objects.filter(user=self.user).exists())

    def test_rating_endpoint_rejects_get_requests(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("interactions:rate_service", args=[self.service.id])
        )

        self.assertEqual(response.status_code, 405)

    def test_user_cannot_open_another_users_order(self):
        order = Order.objects.create(
            user=self.other_user,
            full_name="Other User",
            billing_email="other@example.com",
            billing_address="2 Test Street",
            city="Athens",
            postal_code="12345",
            country="Greece",
            total_price="79.00",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("cart:checkout_success", args=[order.id]))

        self.assertEqual(response.status_code, 404)

    def test_login_does_not_redirect_to_an_external_site(self):
        response = self.client.post(
            reverse("accounts:login") + "?next=https://example.com/steal",
            {
                "username": self.user.username,
                "password": "StrongTestPassword!4826",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(response["Location"].startswith("https://example.com"))

    def test_password_is_hashed(self):
        self.assertNotEqual(self.user.password, "StrongTestPassword!4826")
        self.assertTrue(self.user.check_password("StrongTestPassword!4826"))

    def test_cart_quantity_is_limited(self):
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(cart=cart, service=self.service, quantity=20)
        self.client.force_login(self.user)

        response = self.client.post(reverse("cart:add_to_cart", args=[self.service.id]))

        item.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(item.quantity, 20)

    def test_standard_security_headers_are_present(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        self.assertEqual(response["Cross-Origin-Opener-Policy"], "same-origin")
        self.assertIn("default-src 'self'", response["Content-Security-Policy"])
        self.assertIn("object-src 'none'", response["Content-Security-Policy"])

    def test_service_script_uses_a_csp_nonce(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("catalogue:service_detail", args=[self.service.slug])
        )

        csp_header = response["Content-Security-Policy"]
        self.assertIn("script-src", csp_header)
        self.assertIn("'nonce-", csp_header)
        self.assertContains(response, 'script nonce="')
