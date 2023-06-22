from django.core.management import BaseCommand
from blogapp.models import Category


class Command(BaseCommand):
    """
    Creates categories
    """
    def handle(self, *args, **options):
        self.stdout.write("Create categories")
        categories_names = [
            "roman",
            "note",
            "tragedy",
            "detective",
        ]
        categories = [
            Category(name=category_name)
            for category_name in categories_names
        ]
        result = Category.objects.bulk_create(categories)
        for obj in result:
            print(obj)
        self.stdout.write(self.style.SUCCESS("Categories created"))
