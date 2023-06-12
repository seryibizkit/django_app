from myauth.models import Profile
from django.core.management import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Creates profiles
    """
    def handle(self, *args, **options):
        for user in User.objects.all():
            profile, created = Profile.objects.get_or_create(user=user)
            self.stdout.write("Created profile {}".format(profile.user.first_name))
        self.stdout.write(self.style.SUCCESS("Profiles created"))
