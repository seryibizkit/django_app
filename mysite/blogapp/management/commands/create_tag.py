from django.core.management import BaseCommand
from blogapp.models import Tag


class Command(BaseCommand):
    """
    Creates tags
    """
    def handle(self, *args, **options):
        self.stdout.write("Create tags")
        tags_names = [
            "#history",
            "#funny",
            "#2023",
            "#actual",
            "#to_think"
        ]
        tags = [
            Tag(name=tag_name)
            for tag_name in tags_names
        ]
        result = Tag.objects.bulk_create(tags)
        for obj in result:
            print(obj)
        self.stdout.write(self.style.SUCCESS("Tags created"))
