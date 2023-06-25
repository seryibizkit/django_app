from django.contrib.sitemaps import Sitemap

from .models import Article


class BlogSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Article.objects.filter(pub_date__isnull=False)\
            .order_by("-pub_date")\
            .select_related("author").defer("author__bio")\
            .select_related("category").defer("category__id")\
            .prefetch_related("tags")

    def lastmod(self, obj: Article):
        return obj.pub_date
