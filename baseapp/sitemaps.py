from django.contrib.sitemaps import Sitemap
from django.core.cache import cache
from django.core.paginator import Paginator
from django.urls import reverse
from object.models import *
from authapp.models import *


class HomeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0
    protocol = "https"

    def items(self):
        return ['baseapp:home']

    def location(self, item):
        return reverse(item)

class SoloHomeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0
    protocol = "https"

    def items(self):
        return ['baseapp:solo_home']

    def location(self, item):
        return reverse(item)

class GroupHomeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0
    protocol = "https"

    def items(self):
        return ['baseapp:group_home']

    def location(self, item):
        return reverse(item)


class PostSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0
    protocol = "https"

    def items(self):
        return Post.objects.all().order_by('-created')

    def lastmod(self, obj):
        return obj.updated


class SoloSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0
    protocol = "https"

    def items(self):
        return Solo.objects.all().order_by('-created')

    def lastmod(self, obj):
        return obj.updated


class GroupSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0
    protocol = "https"

    def items(self):
        return Group.objects.all().order_by('-created')

    def lastmod(self, obj):
        return obj.updated


class UserSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0
    protocol = "https"

    def items(self):
        return UserUsername.objects.all().order_by('-created')

    def lastmod(self, obj):
        return obj.updated


sitemaps = {
    'home': HomeSitemap,
    'solo_home': SoloHomeSitemap,
    'group_home': GroupHomeSitemap,
    'post': PostSitemap,
    'solo': SoloSitemap,
    'group': GroupSitemap,
    'user': UserSitemap,
}
