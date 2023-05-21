from django.core.management import BaseCommand
from django.contrib.auth.models import User, Permission, Group


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.get(pk=4)
        group, created = Group.objects.get_or_create(
            name="profile_manager"
        )
        permission_profile = Permission.objects.get(
            codename="view_profile"
        )
        permission_logentry = Permission.objects.get(
            codename="view_logentry"
        )
        # добавление разрешения группе
        group.permissions.add(permission_profile)
        # добавление пользователя в группу
        user.groups.add(group)
        # связать пользователя с разрешением напрямую
        user.user_permissions.add(permission_logentry)

        group.save()
        user.save()
