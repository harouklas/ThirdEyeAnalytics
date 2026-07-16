"""Create the three local demonstration accounts listed in the README."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from accounts.models import Profile


User = get_user_model()


class Command(BaseCommand):
    help = "Create or reset the three local ThirdEye demonstration accounts."

    # Keeping the details together makes each username, role and permission easy to check.
    demo_accounts = (
        {
            "username": "headadmin",
            "password": "HeadAdmin123!",
            "email": "headadmin@example.com",
            "first_name": "Head",
            "last_name": "Administrator",
            "full_name": "Head Administrator",
            "role": Profile.UserRole.HEAD_ADMINISTRATOR,
            "is_staff": True,
            "is_superuser": True,
        },
        {
            "username": "administrator",
            "password": "Admin12345!",
            "email": "administrator@example.com",
            "first_name": "Demo",
            "last_name": "Administrator",
            "full_name": "Administrator",
            "role": Profile.UserRole.ADMINISTRATOR,
            "is_staff": True,
            "is_superuser": False,
        },
        {
            "username": "user",
            "password": "User12345!",
            "email": "user@example.com",
            "first_name": "Demo",
            "last_name": "User",
            "full_name": "Demo User",
            "role": Profile.UserRole.USER,
            "is_staff": False,
            "is_superuser": False,
        },
    )

    def handle(self, *args, **options):
        # These passwords are public in the README, so never create them on a live site.
        if not settings.DEBUG:
            raise CommandError(
                "seed_demo_users only runs locally while DJANGO_DEBUG is True."
            )

        for account in self.demo_accounts:
            # get_or_create avoids duplicate usernames when the command is run again.
            user, created = User.objects.get_or_create(username=account["username"])

            # Reset the local account so its details always match the README.
            user.email = account["email"]
            user.first_name = account["first_name"]
            user.last_name = account["last_name"]
            user.is_active = True
            user.is_staff = account["is_staff"]
            user.is_superuser = account["is_superuser"]
            # set_password hashes the password instead of saving readable text.
            user.set_password(account["password"])
            user.save()

            # The profile contains the readable ThirdEye role shown in the website.
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    "full_name": account["full_name"],
                    "role": account["role"],
                },
            )

            action = "created" if created else "reset"
            self.stdout.write(f"{account['username']}: {action}")

        self.stdout.write(
            self.style.SUCCESS("The three local demonstration accounts are ready.")
        )
