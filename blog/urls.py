from . import views
from django.urls import path
from .feeds import LatestPostsFeed

app_name = 'blog'

urlpatterns = [
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('', views.post_list, name='post_list'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('thanks/', views.thanks, name='thanks'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('<slug:slug>/share/', views.post_share, name='post_share'),
    path('<slug:slug>/comment/', views.post_comment, name='post_comment'),
    path('<slug:category_slug>/', views.category_posts, name='post_list_by_category'),
    path('<slug:category_slug>/<slug:slug>/', views.post_detail, name='post_detail'),
    path('search/', views.search, name='search'),
]
