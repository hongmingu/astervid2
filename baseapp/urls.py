from django.urls import path, re_path
from authapp import views as authviews
from authapp import ajax_views as auth_ajax_views
from baseapp import ajax_views as base_ajax_views
from baseapp import rest_views as base_rest_views
from baseapp import views
from django.views.generic import TemplateView
from baseapp.sitemaps import sitemaps
from django.contrib.sitemaps import views as sitemap_views

app_name = 'baseapp'

urlpatterns = [
    re_path(r'^user/accounts/$', authviews.main_create_log_in, name='main_create_log_in'),

    re_path(r'^create/new/$', views.create_new, name="create_new"),
    re_path(r'^create/group/post/(?P<uuid>([0-9a-f]{32}))/$', views.create_group_post, name="create_group_post"),
    re_path(r'^create/solo/post/(?P<uuid>([0-9a-f]{32}))/$', views.create_solo_post, name="create_solo_post"),

    re_path(r'^update/group/post/(?P<uuid>([0-9a-f]{32}))/$', views.update_group_post, name="update_group_post"),
    re_path(r'^update/solo/post/(?P<uuid>([0-9a-f]{32}))/$', views.update_solo_post, name="update_solo_post"),

    re_path(r'^(?P<user_username>([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?))/$',
            views.user_profile, name='user_profile'),
    re_path(r'^solo/profile/(?P<uuid>([0-9a-f]{32}))/$', views.solo_profile, name="solo_profile"),
    re_path(r'^group/profile/(?P<uuid>([0-9a-f]{32}))/$', views.group_profile, name="group_profile"),

    re_path(r'^post/(?P<uuid>([0-9a-f]{32}))/$', views.post, name='post'),

    re_path(r'^solo/(?P<uuid>([0-9a-f]{32}))/$', views.solo_posts, name="solo_posts"),
    re_path(r'^group/(?P<uuid>([0-9a-f]{32}))/$', views.group_posts, name="group_posts"),

    # --------------------------------------------------------------------------------
    re_path(r'^rest/add/post/$', base_rest_views.add_post, name="rest_ping"),
    re_path(r'^rest/sign_up/$', base_rest_views.sign_up, name="sign_up"),
    re_path(r'^rest/log_in/$', base_rest_views.log_in, name="log_in"),

    re_path(r'^rest/refresh_for_you_pings/$', base_rest_views.refresh_for_you_pings, name="refresh_for_you_pings"),
    re_path(r'^rest/refresh_recommend_pings/$', base_rest_views.refresh_recommend_pings, name="refresh_recommend_pings"),
    re_path(r'^rest/refresh_search_content_pings/$', base_rest_views.refresh_search_content_pings,
            name="refresh_search_content_pings"),
    re_path(r'^rest/refresh_ping_search_result/$', base_rest_views.refresh_ping_search_result,
            name="refresh_ping_search_result"),

    re_path(r'^rest/send_instant_ping/$', base_rest_views.send_instant_ping,
            name="send_instant_ping"),

    re_path(r'^rest/get_follow_feed/$', base_rest_views.get_follow_feed,
            name="get_follow_feed"),
]


from django.conf import settings

if settings.DEBUG:
    urlpatterns += [

    ]
