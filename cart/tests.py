"""Tests that public Viewers cannot access the shopping cart."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from accounts.models import Profile
from catalogue.models import Category, Service, SubCategory

from .forms import CheckoutForm
from .models import Cart, CartItem, Order

User = get_user_model()


class CheckoutFormValidationTests(SimpleTestCase):
    def setUp(self):
        self.valid_data = {
            "full_name": "Demo Customer",
            "billing_email": "billing@example.com",
            "organization": "Demo Academy",
            "billing_address": "12 Football Street",
            "city": "Athens",
            "postal_code": "10558",
            "country": "Greece",
            "vat_number": "EL123456789",
        }

    def form_with(self, **changes):
        data = self.valid_data.copy()
        data.update(changes)
        return CheckoutForm(data=data)

    def test_form_accepts_values_at_their_character_limits(self):
        # The email is exactly 254 characters and respects email label limits.
        maximum_email = (
            f"{'a' * 64}@{'b' * 63}.{'c' * 63}.{'d' * 57}.com"
        )
        form = self.form_with(
            full_name="A" * 150,
            billing_email=maximum_email,
            organization="A" * 150,
            billing_address="1" * 255,
            city="A" * 100,
            postal_code="A" * 20,
            country="A" * 100,
            vat_number="A" * 50,
        )

        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_form_rejects_values_over_their_character_limits(self):
        over_limit_values = {
            "full_name": "A" * 151,
            "billing_email": f"{'a' * 255}@example.com",
            "organization": "A" * 151,
            "billing_address": "1" * 256,
            "city": "A" * 101,
            "postal_code": "A" * 21,
            "country": "A" * 101,
            "vat_number": "A" * 51,
        }

        for field_name, value in over_limit_values.items():
            with self.subTest(field=field_name):
                form = self.form_with(**{field_name: value})
                self.assertFalse(form.is_valid())
                self.assertIn(field_name, form.errors)

    def test_optional_organization_and_vat_number_can_be_blank(self):
        form = self.form_with(organization="", vat_number="")

        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_form_rejects_a_malformed_email_address(self):
        form = self.form_with(billing_email="not-an-email")

        self.assertFalse(form.is_valid())
        self.assertIn("billing_email", form.errors)

    def test_form_rejects_too_short_values(self):
        too_short_values = {
            "full_name": "A",
            "organization": "A",
            "billing_address": "1 A",
            "postal_code": "12",
            "country": "A",
            "vat_number": "EL1",
        }

        for field_name, value in too_short_values.items():
            with self.subTest(field=field_name):
                form = self.form_with(**{field_name: value})
                self.assertFalse(form.is_valid())
                self.assertIn(field_name, form.errors)

    def test_form_rejects_invalid_characters_and_separator_only_codes(self):
        invalid_values = {
            "full_name": "Demo Customer 2",
            "organization": "@@@@@",
            "billing_address": "12 Football Street <script>",
            "city": "Athens@",
            "postal_code": "---",
            "country": "Greece2",
            "vat_number": "-----",
        }

        for field_name, value in invalid_values.items():
            with self.subTest(field=field_name):
                form = self.form_with(**{field_name: value})
                self.assertFalse(form.is_valid())
                self.assertIn(field_name, form.errors)

    def test_form_rejects_repeated_postal_and_vat_separators(self):
        for field_name, value in {
            "postal_code": "SW1A  1AA",
            "vat_number": "EL--123456",
        }.items():
            with self.subTest(field=field_name):
                form = self.form_with(**{field_name: value})
                self.assertFalse(form.is_valid())
                self.assertIn(field_name, form.errors)

    def test_normalization_happens_before_length_and_character_validation(self):
        short_after_normalization = self.form_with(billing_address="1    A")
        decomposed_unicode = self.form_with(full_name="E\u0301lodie Martin")

        self.assertFalse(short_after_normalization.is_valid())
        self.assertIn("billing_address", short_after_normalization.errors)
        self.assertTrue(decomposed_unicode.is_valid(), decomposed_unicode.errors.as_json())
        self.assertEqual(decomposed_unicode.cleaned_data["full_name"], "Élodie Martin")

    def test_form_rejects_line_breaks_and_control_characters(self):
        invalid_values = {
            "full_name": "Demo\nCustomer",
            "organization": "Demo\tAcademy",
            "billing_address": "12\u2028Football Street",
            "city": "Athens\u200b",
            "country": "Gre\r\nece",
            "postal_code": "10558\n",
            "vat_number": "EL123456789\t",
        }

        for field_name, value in invalid_values.items():
            with self.subTest(field=field_name):
                form = self.form_with(**{field_name: value})
                self.assertFalse(form.is_valid())
                self.assertIn(field_name, form.errors)

    def test_form_accepts_international_letters_and_normalizes_values(self):
        form = self.form_with(
            full_name="  Νίκος   Ανδρέου  ",
            organization="  Académie   21  ",
            billing_address="  12 Rue   de l’Église  ",
            city="  São   Paulo  ",
            postal_code="sw1a 1aa",
            country="  Côte   d’Ivoire  ",
            vat_number="el 123-456-789",
        )

        self.assertTrue(form.is_valid(), form.errors.as_json())
        self.assertEqual(form.cleaned_data["full_name"], "Νίκος Ανδρέου")
        self.assertEqual(form.cleaned_data["organization"], "Académie 21")
        self.assertEqual(form.cleaned_data["billing_address"], "12 Rue de l’Église")
        self.assertEqual(form.cleaned_data["city"], "São Paulo")
        self.assertEqual(form.cleaned_data["postal_code"], "SW1A 1AA")
        self.assertEqual(form.cleaned_data["country"], "Côte d’Ivoire")
        self.assertEqual(form.cleaned_data["vat_number"], "EL 123-456-789")

    def test_form_accepts_complex_scripts_and_real_world_localities(self):
        examples = [
            {
                "full_name": "अनिल कुमार",
                "billing_address": "१२ गांधी मार्ग",
                "city": "नई दिल्ली",
                "country": "भारत",
            },
            {
                "full_name": "مُحَمَّد علي",
                "organization": "M+R Analytics",
                "city": "6th of October City",
                "country": "Egypt",
            },
            {
                "full_name": "علی‌رضا رضایی",
                "city": "Y",
                "country": "France",
            },
        ]

        for changes in examples:
            with self.subTest(changes=changes):
                form = self.form_with(**changes)
                self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_rendered_fields_include_browser_constraints(self):
        form = CheckoutForm()

        full_name_html = str(form["full_name"])
        postal_code_html = str(form["postal_code"])
        billing_address_html = str(form["billing_address"])
        vat_number_html = str(form["vat_number"])

        self.assertIn('minlength="2"', full_name_html)
        self.assertIn('maxlength="150"', full_name_html)
        self.assertIn('autocomplete="name"', full_name_html)
        self.assertIn('minlength="5"', billing_address_html)
        self.assertIn('maxlength="255"', billing_address_html)
        self.assertIn('autocomplete="street-address"', billing_address_html)
        self.assertIn(
            'pattern="[A-Za-z0-9]+(?:[ \\-][A-Za-z0-9]+)*"',
            postal_code_html,
        )
        self.assertIn('autocomplete="postal-code"', postal_code_html)
        self.assertIn('minlength="5"', vat_number_html)
        self.assertIn('maxlength="50"', vat_number_html)
        self.assertIn(
            'pattern="[A-Za-z0-9]+(?:[ .\\-][A-Za-z0-9]+)*"',
            vat_number_html,
        )

    def test_invalid_widget_describes_its_help_and_error_messages(self):
        form = self.form_with(postal_code="---")
        self.assertFalse(form.is_valid())

        postal_code_html = str(form["postal_code"])
        self.assertIn('aria-describedby="', postal_code_html)
        self.assertIn("id_postal_code_helptext", postal_code_html)
        self.assertIn("id_postal_code_error", postal_code_html)


class PublicViewerCartPermissionTests(TestCase):
    # The cart is a member feature, so a Viewer should be redirected to login.
    def test_public_viewer_is_redirected_to_login(self):
        response = self.client.get(reverse("cart:cart_detail"))

        login_url = reverse("accounts:login")
        cart_url = reverse("cart:cart_detail")
        self.assertRedirects(response, f"{login_url}?next={cart_url}")


class CheckoutFormTests(TestCase):
    def setUp(self):
        # Create a user, profile, service, and cart line shared by checkout tests.
        self.user = User.objects.create_user(
            username="checkoutuser",
            email="customer@example.com",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.user,
            full_name="Demo Customer",
            organization="Demo Academy",
        )
        category = Category.objects.create(name="Player Analysis", slug="player-analysis")
        subcategory = SubCategory.objects.create(
            category=category,
            name="Tracking",
            slug="tracking",
        )
        service = Service.objects.create(
            category=category,
            subcategory=subcategory,
            name="Player Tracking Test",
            slug="player-tracking-test",
            short_description="A test tracking service.",
            description="Used to test checkout billing information.",
            analysis_type=Service.AnalysisType.TRACKING,
            skill_level=Service.SkillLevel.ACADEMY,
            video_type=Service.VideoType.FULL_MATCH,
            delivery_time=Service.DeliveryTime.HOURS_48,
            output_format=Service.OutputFormat.PDF_REPORT,
            price=Decimal("99.00"),
        )
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, service=service)
        self.client.force_login(self.user)
        # This is one complete valid billing form submission.
        self.checkout_data = {
            "full_name": "Demo Customer",
            "billing_email": "billing@example.com",
            "organization": "Demo Academy",
            "billing_address": "12 Football Street",
            "city": "Athens",
            "postal_code": "10558",
            "country": "Greece",
            "vat_number": "EL123456789",
        }

    def test_checkout_form_prefills_profile_details(self):
        response = self.client.get(reverse("cart:checkout"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Demo Customer")
        self.assertContains(response, "customer@example.com")
        self.assertContains(response, "Demo Academy")

    def test_checkout_requires_billing_address(self):
        # Remove one required value and confirm that no Order is created.
        invalid_data = self.checkout_data.copy()
        invalid_data["billing_address"] = ""

        response = self.client.post(reverse("cart:checkout"), invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_rejects_invalid_postal_code_and_keeps_cart(self):
        invalid_data = self.checkout_data.copy()
        invalid_data["postal_code"] = "---"

        response = self.client.post(reverse("cart:checkout"), invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid postal code")
        self.assertContains(response, 'id="id_postal_code_helptext"')
        self.assertContains(response, 'id="id_postal_code_error"')
        self.assertEqual(Order.objects.count(), 0)
        self.assertTrue(self.cart.items.exists())

    def test_checkout_normalizes_billing_details_before_saving(self):
        normalized_data = self.checkout_data.copy()
        normalized_data.update(
            {
                "full_name": "  Demo   Customer  ",
                "organization": "  Demo   Academy  ",
                "billing_address": "  12 Football   Street  ",
                "city": "  New   York  ",
                "postal_code": "sw1a 1aa",
                "country": "  United   Kingdom  ",
                "vat_number": "gb 123-456-789",
            }
        )

        response = self.client.post(reverse("cart:checkout"), normalized_data)

        order = Order.objects.get(user=self.user)
        self.assertRedirects(
            response,
            reverse("cart:checkout_success", args=[order.id]),
        )
        self.assertEqual(order.full_name, "Demo Customer")
        self.assertEqual(order.organization, "Demo Academy")
        self.assertEqual(order.billing_address, "12 Football Street")
        self.assertEqual(order.city, "New York")
        self.assertEqual(order.postal_code, "SW1A 1AA")
        self.assertEqual(order.country, "United Kingdom")
        self.assertEqual(order.vat_number, "GB 123-456-789")

    def test_checkout_saves_billing_details_and_clears_cart(self):
        response = self.client.post(reverse("cart:checkout"), self.checkout_data)

        order = Order.objects.get(user=self.user)
        self.assertRedirects(
            response,
            reverse("cart:checkout_success", args=[order.id]),
        )
        self.assertEqual(order.billing_email, "billing@example.com")
        self.assertEqual(order.billing_address, "12 Football Street")
        self.assertEqual(order.city, "Athens")
        self.assertEqual(order.postal_code, "10558")
        self.assertEqual(order.country, "Greece")
        self.assertEqual(order.vat_number, "EL123456789")
        # The order keeps the item while the user's active cart becomes empty.
        self.assertEqual(order.items.count(), 1)
        self.assertFalse(self.cart.items.exists())
