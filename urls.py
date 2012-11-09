from django.conf.urls.defaults import patterns, include, url
from django.views.generic.base import RedirectView
from core.views import *
from django.contrib import admin
from djrill import DjrillAdminSite
from django.conf import settings

admin.site = DjrillAdminSite()
admin.autodiscover()

urlpatterns = patterns('core.views',

    url(r'^$', 'home', name='home'),
    url(r'^bakery', 'bakery', name='bakery'),
    url(r'^about', 'about', name='about'),
    url(r'^make_my_cookies', 'mmc', name='mmc'),
    url(r'^contact', 'contact', name='contact'),
    url(r'^checkout', 'checkout', name='checkout'),
    url(r'^secretpathtoadmin/', include(admin.site.urls)),
    (r'^favicon\.ico$', RedirectView.as_view(url='/static/img/favicon.ico')),
    url(r'^category/(?P<id>\w+)/', 'category', name='category'),
    url(r'^item/(?P<id>\w+)/', 'item', name='item'),
    url(r'^item_to_cart/(?P<id>\w+)/', 'item_to_cart', name='item_to_cart'),
    url(r'^order_confirmed/(?P<id>\w+)/', 'order_confirmed', name='order_confirmed'),
    url(r'^remove_item_from_cart/(?P<id>\w+)/', 'remove_item_from_cart', name='remove_item_from_cart'),
    url(r'^foward/', 'foward', name='foward'),
    url(r'^terms/', 'terms', name='terms'),
    url(r'^custom_css/', 'custom_css', name='custom_css'),
    url(r'^custom_js/', 'custom_js', name='custom_js')
)

urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
)
