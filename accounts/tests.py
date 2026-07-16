"""Tests for registration, dashboards, roles, and management permissions."""

from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse

from cart.models import Order, OrderItem
from catalogue.models import Category, Service, SubCategory
from interactions.models import Rating

from .forms import ProfileForm, RegistrationForm
from .models import Profile

User = get_user_model()


class RegistrationValidationTests(TestCase):
    def valid_data(self):
        return {
            "username": "player.1",
            "email": "player@example.com",
            "password1": "StrongPass7!",
            "password2": "StrongPass7!",
            "first_name": "Nikos",
            "last_name": "Andreou",
            "phone_country_code": Profile.PhoneCountry.CYPRUS,
            "phone_number": "99123456",
            "organization": "ThirdEye Academy",
            "sport_role": Profile.SportRole.PLAYER,
            "favorite_analysis_type": "Tracking",
            "bio": "Academy player interested in performance analysis.",
        }

    def test_valid_registration_data_is_accepted(self):
        form = RegistrationForm(data=self.valid_data())

        self.assertTrue(form.is_valid(), form.errors)

    def test_username_rules(self):
        invalid_usernames = [
            "abcdefghijk",
            "player-test",
            "player_",
            "player.",
        ]

        for username in invalid_usernames:
            with self.subTest(username=username):
                data = self.valid_data()
                data["username"] = username
                form = RegistrationForm(data=data)
                self.assertFalse(form.is_valid())
                self.assertIn("username", form.errors)

    def test_username_accepts_dot_and_underscore(self):
        data = self.valid_data()
        data["username"] = "eye_user.1"

        form = RegistrationForm(data=data)

        self.assertTrue(form.is_valid(), form.errors)

    def test_email_must_have_a_valid_format(self):
        data = self.valid_data()
        data["email"] = "not-an-email"

        form = RegistrationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_password_complexity_rules(self):
        invalid_passwords = [
            "PASSWORD9!",
            "password9!",
            "Password!",
            "Password9",
            "Pa1!aaa",
        ]

        for password in invalid_passwords:
            with self.subTest(password=password):
                data = self.valid_data()
                data["password1"] = password
                data["password2"] = password
                form = RegistrationForm(data=data)
                self.assertFalse(form.is_valid())
                self.assertIn("password1", form.errors)

    def test_password_cannot_match_username(self):
        data = self.valid_data()
        data["username"] = "Test.user1"
        data["password1"] = "Test.user1"
        data["password2"] = "Test.user1"

        form = RegistrationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("same as your username", str(form.errors["password1"]))

    def test_password_cannot_match_email(self):
        data = self.valid_data()
        data["email"] = "Test1!@x.co"
        data["password1"] = data["email"]
        data["password2"] = data["email"]

        form = RegistrationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("same as your email", str(form.errors["password1"]))

    def test_name_and_surname_accept_letters_only(self):
        data = self.valid_data()
        data["first_name"] = "Nikos2"
        data["last_name"] = "Andreou-Smith"

        form = RegistrationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertIn("last_name", form.errors)

    def test_phone_number_accepts_digits_only(self):
        data = self.valid_data()
        data["phone_number"] = "+357 9912-3456"

        form = RegistrationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)

    def test_organization_and_bio_limits(self):
        data = self.valid_data()
        data["organization"] = "o" * 26
        data["bio"] = "b" * 251

        form = RegistrationForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("organization", form.errors)
        self.assertIn("bio", form.errors)

    def test_profile_edit_uses_the_same_personal_detail_rules(self):
        user = User.objects.create_user(
            username="profile.1",
            email="profile@example.com",
            password="StrongPass7!",
        )
        profile = Profile.objects.create(user=user, full_name="Nikos Andreou")
        form = ProfileForm(
            data={
                "first_name": "Nikos2",
                "last_name": "Andreou!",
                "email": "not-an-email",
                "phone_country_code": Profile.PhoneCountry.GREECE,
                "phone_number": "210-1234567",
                "organization": "o" * 26,
                "sport_role": Profile.SportRole.PLAYER,
                "favorite_analysis_type": "Tracking",
                "bio": "b" * 251,
            },
            instance=profile,
            user=user,
        )

        self.assertFalse(form.is_valid())
        for field_name in [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "organization",
            "bio",
        ]:
            self.assertIn(field_name, form.errors)

    def test_registration_saves_separate_names_and_phone_country(self):
        data = self.valid_data()

        response = self.client.post(reverse("accounts:register"), data)

        self.assertRedirects(response, reverse("accounts:dashboard"))
        user = User.objects.get(username=data["username"])
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.last_name, data["last_name"])
        self.assertEqual(user.profile.full_name, "Nikos Andreou")
        self.assertEqual(user.profile.phone_country_code, Profile.PhoneCountry.CYPRUS)


class DashboardProductRatingsTests(TestCase):
    def setUp(self):
        category = Category.objects.create(
            name="Dashboard Analysis",
            slug="dashboard-analysis",
        )
        subcategory = SubCategory.objects.create(
            category=category,
            name="Dashboard Reports",
            slug="dashboard-reports",
        )
        self.own_service = self.create_service(
            category,
            subcategory,
            name="Personal Tracking Review",
            slug="personal-tracking-review",
        )
        other_service = self.create_service(
            category,
            subcategory,
            name="Other User Review",
            slug="other-user-review",
        )

        self.user = User.objects.create_user(username="ratings.user")
        Profile.objects.create(user=self.user, full_name="Ratings User")
        other_user = User.objects.create_user(username="other.rater")
        Profile.objects.create(user=other_user, full_name="Other Rater")

        self.own_rating = Rating.objects.create(
            user=self.user,
            service=self.own_service,
            score=Rating.Score.FOUR,
        )
        Rating.objects.create(
            user=other_user,
            service=other_service,
            score=Rating.Score.TWO,
        )

    @staticmethod
    def create_service(category, subcategory, *, name, slug):
        return Service.objects.create(
            category=category,
            subcategory=subcategory,
            name=name,
            slug=slug,
            short_description="Dashboard rating test service.",
            description="Service used to verify dashboard product ratings.",
            analysis_type=Service.AnalysisType.TRACKING,
            skill_level=Service.SkillLevel.ACADEMY,
            video_type=Service.VideoType.FULL_MATCH,
            delivery_time=Service.DeliveryTime.HOURS_24,
            output_format=Service.OutputFormat.PDF_REPORT,
            price="49.00",
        )

    def test_dashboard_shows_only_the_logged_in_users_ratings(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["user_ratings"]), [self.own_rating])
        self.assertContains(response, "Your Product Ratings")
        self.assertContains(response, self.own_service.name)
        self.assertContains(response, "4 stars")

    def test_dashboard_shows_product_rating_empty_state(self):
        self.own_rating.delete()
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["user_ratings"]), [])
        self.assertContains(response, "No product ratings yet.")


@override_settings(DEBUG=True)
class SeedDemoUsersCommandTests(TestCase):
    """The downloaded project can create its documented local demo accounts."""

    def run_command(self):
        # Capture the text so command output does not make the test results noisy.
        output = StringIO()
        call_command("seed_demo_users", stdout=output)
        return output.getvalue()

    def test_command_creates_the_three_accounts_with_the_correct_access(self):
        output = self.run_command()

        expected_accounts = {
            "headadmin": {
                "password": "HeadAdmin123!",
                "full_name": "Head Administrator",
                "role": Profile.UserRole.HEAD_ADMINISTRATOR,
                "is_staff": True,
                "is_superuser": True,
            },
            "administrator": {
                "password": "Admin12345!",
                "full_name": "Administrator",
                "role": Profile.UserRole.ADMINISTRATOR,
                "is_staff": True,
                "is_superuser": False,
            },
            "user": {
                "password": "User12345!",
                "full_name": "Demo User",
                "role": Profile.UserRole.USER,
                "is_staff": False,
                "is_superuser": False,
            },
        }

        self.assertEqual(User.objects.count(), 3)
        for username, expected in expected_accounts.items():
            with self.subTest(username=username):
                user = User.objects.select_related("profile").get(username=username)
                self.assertTrue(user.check_password(expected["password"]))
                self.assertTrue(user.is_active)
                self.assertEqual(user.is_staff, expected["is_staff"])
                self.assertEqual(user.is_superuser, expected["is_superuser"])
                self.assertEqual(user.profile.full_name, expected["full_name"])
                self.assertEqual(user.profile.role, expected["role"])

        self.assertIn("The three local demonstration accounts are ready.", output)

    def test_running_the_command_again_resets_accounts_without_duplicates(self):
        self.run_command()
        administrator = User.objects.get(username="administrator")
        administrator.is_staff = False
        administrator.set_password("ChangedPassword9!")
        administrator.save()
        administrator.profile.role = Profile.UserRole.USER
        administrator.profile.save(update_fields=["role"])

        output = self.run_command()

        administrator.refresh_from_db()
        administrator.profile.refresh_from_db()
        self.assertEqual(User.objects.count(), 3)
        self.assertTrue(administrator.check_password("Admin12345!"))
        self.assertTrue(administrator.is_staff)
        self.assertEqual(
            administrator.profile.role,
            Profile.UserRole.ADMINISTRATOR,
        )
        self.assertIn("administrator: reset", output)

    @override_settings(DEBUG=False)
    def test_command_refuses_to_create_public_production_passwords(self):
        with self.assertRaisesMessage(CommandError, "only runs locally"):
            call_command("seed_demo_users")

        self.assertFalse(User.objects.exists())


class RoleSecurityTests(TestCase):
    def setUp(self):
        # Create one account for each registered access level used by the tests.
        self.head_admin = User.objects.create_superuser(
            username="headadmin",
            email="head@example.com",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.head_admin,
            full_name="Head Admin",
            role=Profile.UserRole.HEAD_ADMINISTRATOR,
        )

        self.administrator = User.objects.create_user(
            username="administrator",
            password="TestPassword123!",
            is_staff=True,
        )
        Profile.objects.create(
            user=self.administrator,
            full_name="Administrator",
            role=Profile.UserRole.ADMINISTRATOR,
        )

        self.regular_user = User.objects.create_user(
            username="regularuser",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.regular_user,
            full_name="Regular User",
        )

    def test_new_profile_uses_user_role_by_default(self):
        self.assertEqual(self.regular_user.profile.role, Profile.UserRole.USER)

    def test_regular_user_cannot_open_management_dashboard(self):
        # A normal User is logged in but still does not have staff permission.
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse("accounts:management_dashboard"))
        self.assertRedirects(response, reverse("accounts:dashboard"))

    def test_administrator_can_open_management_dashboard(self):
        self.client.force_login(self.administrator)
        response = self.client.get(reverse("accounts:management_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_head_administrator_sees_advanced_admin_integration(self):
        self.client.force_login(self.head_admin)
        response = self.client.get(reverse("accounts:management_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Advanced administration")
        self.assertContains(response, reverse("admin:index"))
        self.assertContains(response, reverse("admin:auth_user_changelist"))
        self.assertContains(response, reverse("admin:catalogue_service_changelist"))
        self.assertContains(response, reverse("admin:cart_order_changelist"))
        self.assertContains(response, reverse("admin:interactions_rating_changelist"))

    def test_administrator_does_not_see_advanced_admin_integration(self):
        self.client.force_login(self.administrator)
        response = self.client.get(reverse("accounts:management_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Advanced administration")
        self.assertNotContains(response, reverse("admin:index"))

    def test_head_administrator_can_open_django_admin(self):
        self.client.force_login(self.head_admin)
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ThirdEye Head Administration")
        self.assertContains(response, reverse("accounts:management_dashboard"))

    def test_administrator_cannot_open_django_admin_directly(self):
        self.client.force_login(self.administrator)
        admin_index = reverse("admin:index")
        response = self.client.get(admin_index)

        self.assertRedirects(
            response,
            f"{reverse('admin:login')}?next={admin_index}",
        )

    def test_administrator_credentials_are_rejected_by_admin_login(self):
        response = self.client.post(
            reverse("admin:login"),
            {
                "username": "administrator",
                "password": "TestPassword123!",
                "next": reverse("admin:index"),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Only Head Administrators can access advanced administration.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_head_administrator_can_sign_in_through_admin_login(self):
        response = self.client.post(
            reverse("admin:login"),
            {
                "username": "headadmin",
                "password": "TestPassword123!",
                "next": reverse("admin:index"),
            },
        )

        self.assertRedirects(response, reverse("admin:index"))
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.head_admin.id,
        )

    def test_head_administrator_can_open_each_admin_shortcut(self):
        self.client.force_login(self.head_admin)

        for url_name in (
            "admin:auth_user_changelist",
            "admin:catalogue_service_changelist",
            "admin:cart_order_changelist",
            "admin:interactions_rating_changelist",
        ):
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)

    def test_administrator_cannot_open_admin_shortcuts_directly(self):
        self.client.force_login(self.administrator)

        for url_name in (
            "admin:auth_user_changelist",
            "admin:catalogue_service_changelist",
            "admin:cart_order_changelist",
            "admin:interactions_rating_changelist",
        ):
            with self.subTest(url_name=url_name):
                protected_url = reverse(url_name)
                response = self.client.get(protected_url)
                self.assertRedirects(
                    response,
                    f"{reverse('admin:login')}?next={protected_url}",
                )

    def test_inactive_head_administrator_cannot_open_django_admin(self):
        self.head_admin.is_active = False
        self.head_admin.save(update_fields=["is_active"])
        self.client.force_login(self.head_admin)

        admin_index = reverse("admin:index")
        response = self.client.get(admin_index)

        self.assertRedirects(
            response,
            f"{reverse('admin:login')}?next={admin_index}",
        )

    def test_head_administrator_can_change_a_user_role(self):
        self.client.force_login(self.head_admin)
        response = self.client.post(
            reverse(
                "accounts:management_user_role_update",
                args=[self.regular_user.id],
            ),
            {"role": Profile.UserRole.ADMINISTRATOR},
        )

        self.assertRedirects(response, reverse("accounts:management_users"))
        self.regular_user.profile.refresh_from_db()
        self.regular_user.refresh_from_db()
        # Check both the readable role and the Django permission flags.
        self.assertEqual(self.regular_user.profile.role, Profile.UserRole.ADMINISTRATOR)
        self.assertTrue(self.regular_user.is_staff)
        self.assertFalse(self.regular_user.is_superuser)

    def test_head_administrator_sees_role_controls(self):
        self.client.force_login(self.head_admin)
        response = self.client.get(reverse("accounts:management_users"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Head Administrator")
        self.assertNotContains(response, 'value="viewer"')
        self.assertContains(
            response,
            reverse(
                "accounts:management_user_role_update",
                args=[self.regular_user.id],
            ),
        )

    def test_administrator_cannot_change_a_user_role(self):
        # is_staff opens management pages, but only is_superuser can change roles.
        self.client.force_login(self.administrator)
        response = self.client.post(
            reverse(
                "accounts:management_user_role_update",
                args=[self.regular_user.id],
            ),
            {"role": Profile.UserRole.ADMINISTRATOR},
        )

        self.assertRedirects(response, reverse("accounts:management_users"))
        self.regular_user.profile.refresh_from_db()
        self.assertEqual(self.regular_user.profile.role, Profile.UserRole.USER)

    def test_administrator_does_not_see_role_controls(self):
        self.client.force_login(self.administrator)
        response = self.client.get(reverse("accounts:management_users"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            reverse(
                "accounts:management_user_role_update",
                args=[self.regular_user.id],
            ),
        )


class ManagementCatalogueTests(TestCase):
    """Tests for staff catalogue editing and safe deletion."""

    def setUp(self):
        self.administrator = User.objects.create_user(
            username="catalogueadmin",
            password="TestPassword123!",
            is_staff=True,
        )
        Profile.objects.create(
            user=self.administrator,
            full_name="Catalogue Admin",
            role=Profile.UserRole.ADMINISTRATOR,
        )
        self.regular_user = User.objects.create_user(
            username="catalogueuser",
            password="TestPassword123!",
        )
        Profile.objects.create(
            user=self.regular_user,
            full_name="Catalogue User",
        )
        self.category = Category.objects.create(
            name="Match Analysis",
            slug="match-analysis",
        )
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            name="Tactical Reports",
            slug="tactical-reports",
        )

    def create_service(self, name="Tactical Report"):
        """Create one complete service for edit and protection tests."""
        return Service.objects.create(
            category=self.category,
            subcategory=self.subcategory,
            name=name,
            slug=name.lower().replace(" ", "-"),
            short_description="A short tactical report.",
            description="A complete tactical report for one football match.",
            analysis_type=Service.AnalysisType.TACTICAL,
            skill_level=Service.SkillLevel.PROFESSIONAL,
            video_type=Service.VideoType.FULL_MATCH,
            delivery_time=Service.DeliveryTime.HOURS_48,
            output_format=Service.OutputFormat.PDF_REPORT,
            price="99.00",
        )

    def test_staff_can_delete_service_after_post_confirmation(self):
        service = self.create_service()
        delete_url = reverse(
            "accounts:management_service_delete",
            args=[service.id],
        )
        self.client.force_login(self.administrator)

        # GET only shows the confirmation page and must not change the database.
        confirmation = self.client.get(delete_url)
        self.assertEqual(confirmation.status_code, 200)
        self.assertContains(confirmation, "Delete Tactical Report?")
        self.assertTrue(Service.objects.filter(id=service.id).exists())

        response = self.client.post(delete_url, follow=True)
        self.assertRedirects(response, reverse("accounts:management_services"))
        self.assertFalse(Service.objects.filter(id=service.id).exists())
        self.assertContains(response, "Tactical Report has been deleted.")

    def test_service_in_saved_order_cannot_be_deleted(self):
        service = self.create_service()
        order = Order.objects.create(
            user=self.administrator,
            full_name="Catalogue Admin",
            billing_email="admin@example.com",
            billing_address="1 Test Street",
            city="Athens",
            postal_code="11111",
            country="Greece",
            total_price="99.00",
        )
        OrderItem.objects.create(
            order=order,
            service=service,
            service_name=service.name,
            price=service.price,
        )
        self.client.force_login(self.administrator)

        response = self.client.post(
            reverse("accounts:management_service_delete", args=[service.id]),
            follow=True,
        )

        self.assertTrue(Service.objects.filter(id=service.id).exists())
        self.assertContains(response, "cannot be deleted because it is part of a saved order")

    def test_staff_can_edit_category(self):
        self.client.force_login(self.administrator)
        response = self.client.post(
            reverse("accounts:management_category_edit", args=[self.category.id]),
            {
                "name": "Updated Analysis",
                "slug": "",
                "description": "Updated category details.",
            },
        )

        self.assertRedirects(response, reverse("accounts:management_categories"))
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, "Updated Analysis")
        self.assertEqual(self.category.slug, "updated-analysis")
        self.assertEqual(self.category.description, "Updated category details.")

    def test_staff_can_edit_subcategory(self):
        self.client.force_login(self.administrator)
        response = self.client.post(
            reverse(
                "accounts:management_subcategory_edit",
                args=[self.subcategory.id],
            ),
            {
                "category": self.category.id,
                "name": "Updated Reports",
                "slug": "",
                "description": "Updated sub-category details.",
            },
        )

        self.assertRedirects(response, reverse("accounts:management_categories"))
        self.subcategory.refresh_from_db()
        self.assertEqual(self.subcategory.name, "Updated Reports")
        self.assertEqual(self.subcategory.slug, "updated-reports")
        self.assertEqual(
            self.subcategory.description,
            "Updated sub-category details.",
        )

    def test_used_subcategory_cannot_move_to_another_category(self):
        self.create_service()
        other_category = Category.objects.create(
            name="Player Analysis",
            slug="player-analysis",
        )
        self.client.force_login(self.administrator)

        response = self.client.post(
            reverse(
                "accounts:management_subcategory_edit",
                args=[self.subcategory.id],
            ),
            {
                "category": other_category.id,
                "name": self.subcategory.name,
                "slug": self.subcategory.slug,
                "description": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot move because one or more services use it")
        self.subcategory.refresh_from_db()
        self.assertEqual(self.subcategory.category, self.category)

    def test_staff_can_delete_unused_category_and_its_subcategories(self):
        category_id = self.category.id
        subcategory_id = self.subcategory.id
        self.client.force_login(self.administrator)

        response = self.client.post(
            reverse("accounts:management_category_delete", args=[category_id]),
            follow=True,
        )

        self.assertFalse(Category.objects.filter(id=category_id).exists())
        self.assertFalse(SubCategory.objects.filter(id=subcategory_id).exists())
        self.assertContains(response, "Match Analysis category has been deleted.")

    def test_staff_can_delete_unused_subcategory(self):
        subcategory_id = self.subcategory.id
        self.client.force_login(self.administrator)

        response = self.client.post(
            reverse(
                "accounts:management_subcategory_delete",
                args=[subcategory_id],
            ),
            follow=True,
        )

        self.assertFalse(SubCategory.objects.filter(id=subcategory_id).exists())
        self.assertTrue(Category.objects.filter(id=self.category.id).exists())
        self.assertContains(response, "Tactical Reports sub-category has been deleted.")

    def test_category_delete_pages_do_not_delete_on_get(self):
        self.client.force_login(self.administrator)

        category_response = self.client.get(
            reverse(
                "accounts:management_category_delete",
                args=[self.category.id],
            )
        )
        subcategory_response = self.client.get(
            reverse(
                "accounts:management_subcategory_delete",
                args=[self.subcategory.id],
            )
        )

        self.assertEqual(category_response.status_code, 200)
        self.assertEqual(subcategory_response.status_code, 200)
        self.assertTrue(Category.objects.filter(id=self.category.id).exists())
        self.assertTrue(SubCategory.objects.filter(id=self.subcategory.id).exists())

    def test_category_used_by_service_cannot_be_deleted(self):
        service = self.create_service()
        self.client.force_login(self.administrator)

        response = self.client.post(
            reverse(
                "accounts:management_category_delete",
                args=[self.category.id],
            ),
            follow=True,
        )

        self.assertTrue(Category.objects.filter(id=self.category.id).exists())
        self.assertTrue(Service.objects.filter(id=service.id).exists())
        self.assertContains(response, "cannot be deleted because it or one of its")
        self.assertContains(response, "sub-categories is used by a service")

    def test_subcategory_used_by_service_cannot_be_deleted(self):
        service = self.create_service()
        self.client.force_login(self.administrator)

        response = self.client.post(
            reverse(
                "accounts:management_subcategory_delete",
                args=[self.subcategory.id],
            ),
            follow=True,
        )

        self.assertTrue(SubCategory.objects.filter(id=self.subcategory.id).exists())
        self.assertTrue(Service.objects.filter(id=service.id).exists())
        self.assertContains(response, "cannot be deleted because it is used by a service")

    def test_regular_user_cannot_change_catalogue_management_data(self):
        service = self.create_service()
        self.client.force_login(self.regular_user)

        protected_requests = [
            (
                reverse("accounts:management_service_delete", args=[service.id]),
                {},
            ),
            (
                reverse("accounts:management_category_edit", args=[self.category.id]),
                {"name": "Changed", "slug": "changed", "description": ""},
            ),
            (
                reverse("accounts:management_category_delete", args=[self.category.id]),
                {},
            ),
            (
                reverse(
                    "accounts:management_subcategory_edit",
                    args=[self.subcategory.id],
                ),
                {
                    "category": self.category.id,
                    "name": "Changed",
                    "slug": "changed",
                    "description": "",
                },
            ),
            (
                reverse(
                    "accounts:management_subcategory_delete",
                    args=[self.subcategory.id],
                ),
                {},
            ),
        ]

        for url, data in protected_requests:
            with self.subTest(url=url):
                response = self.client.post(url, data)
                self.assertRedirects(response, reverse("accounts:dashboard"))

        # None of the rejected requests should change or remove the records.
        self.category.refresh_from_db()
        self.subcategory.refresh_from_db()
        self.assertEqual(self.category.name, "Match Analysis")
        self.assertEqual(self.subcategory.name, "Tactical Reports")
        self.assertTrue(Service.objects.filter(id=service.id).exists())
