"""Add the three registered account roles to user profiles."""

from django.conf import settings
from django.db import migrations, models


def set_existing_user_roles(apps, schema_editor):
    """Match existing Django staff flags to the new profile roles."""

    user_app, user_model = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(user_app, user_model)
    Profile = apps.get_model("accounts", "Profile")

    for user in User.objects.all():
        if user.is_superuser:
            role = "head_administrator"
        elif user.is_staff:
            role = "administrator"
        else:
            role = "user"

        profile, _created = Profile.objects.get_or_create(
            user=user,
            defaults={"full_name": user.username, "role": role},
        )
        if profile.role != role:
            profile.role = role
            profile.save(update_fields=["role"])


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="role",
            field=models.CharField(
                choices=[
                    ("head_administrator", "Head Administrator"),
                    ("administrator", "Administrator"),
                    ("user", "User"),
                ],
                default="user",
                max_length=30,
            ),
        ),
        migrations.RunPython(set_existing_user_roles, migrations.RunPython.noop),
    ]
