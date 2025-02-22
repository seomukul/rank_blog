from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from blog.sitemaps import PostSitemap
from blog.feeds import LatestPostsFeed  # Import the feed
from django.conf import settings
from django.conf.urls.static import static

# Define the sitemaps dictionary
sitemaps = {
    'posts': PostSitemap,
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('', include('blog.urls', namespace='blog')),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])


# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


