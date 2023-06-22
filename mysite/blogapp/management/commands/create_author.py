from django.core.management import BaseCommand
from blogapp.models import Author


class Command(BaseCommand):
    """
    Creates authorss
    """
    def handle(self, *args, **options):
        self.stdout.write("Create authors")
        authors = [
            {"name": "Tolstoy",
             "bio": "Russian writer (War and Peace)."},
            {"name": "Nabokov",
             "bio": "Russian writer lived in New York."},
            {"name": "Zamyatin",
             "bio": "Russian writer"},
        ]
        authors_to_create = [
            Author(name=author.get("name"), bio=author.get("bio"))
            for author in authors
        ]
        result = Author.objects.bulk_create(authors_to_create)
        for obj in result:
            print(obj)
        self.stdout.write(self.style.SUCCESS("Authors created"))
