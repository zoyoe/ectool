from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('ebayapi',
  (r'^exporttoebay/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/','ebay.exporttoebay'),
  (r'^syncwithebay/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/','ebay.syncwithebay'),
  (r'^relisttoebay/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/','ebay.relisttoebay'),
  (r'^fetchcategories/$', 'ebay.fetchcategory'),
  (r'^auth/$', 'ebay.auth'),
  (r'^authfail/$', 'ebay.authfail'),
  (r'^logoutebay/$', 'ebay.logoutebay'),
  (r'^authsuccess/$', 'ebay.authsuccess'),
  )

