from django.views.generic import ListView

from .models import Article


class ArticleListView(ListView):
    template_name = 'blogapp/articles_list.html'
    context_object_name = "articles"
    queryset = (
        Article.objects.select_related("author").defer("author__bio")
        .select_related("category").defer("category__id")
        .prefetch_related("tags").all()
    )
