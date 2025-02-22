from django.contrib.sitemaps import Sitemap
from .models import Post

class PostSitemap(Sitemap):
    changefreq = 'weekly'  # How often the post changes
    priority = 0.9  # Priority level of the post

    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.updated
