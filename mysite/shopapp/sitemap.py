from django.contrib.sitemaps import Sitemap

from .models import Product


class ShopSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Product.objects.defer("preview").filter(archived__isnull=False)\
            .order_by("-created_at")

    @classmethod
    def lastmod(cls, obj: Product):
        return obj.created_at
