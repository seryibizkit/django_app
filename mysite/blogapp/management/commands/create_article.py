from django.core.management import BaseCommand
from django.db import transaction

from blogapp.models import Article, Tag, Author, Category
from typing import Sequence
import random


class Command(BaseCommand):
    """
    Creates articles
    """

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Create articles")
        articles = []
        for i in range(5):
            author = Author.objects.get(id=random.randint(1, 3))
            content = "Some text {}".format(random.randint(1, 1000))
            title = "Title #{}".format(random.randint(1, 10))
            category = Category.objects.get(id=random.randint(1, 4))
            articles.append(Article(author=author, content=content,
                                    title=title, category=category))
        result = Article.objects.bulk_create(articles)
        tags: Sequence[Tag] = Tag.objects.only("id").all()
        created_articles = Article.objects.all()
        for art in created_articles:
            for tag in tags:
                art.tags.add(tag)
        for obj in result:
            print(obj)
        self.stdout.write(self.style.SUCCESS("Articles created"))
