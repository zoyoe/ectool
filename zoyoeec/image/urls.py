from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('image',
  (r'^addimage/','admin.addimage'),
  (r'^addimages/(?P<supplier>[a-zA-Z\d_]+)/$','admin.addimages'), ## Is this still usefull ?
  (r'^view/uploadimages/$','image.view.uploadimages'),
  (r'^rest/uploadimage/(?P<supplier>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/(?P<index>[\d]+)/','image.uploadimage'),
  (r'^rest/rotateimage/(?P<supplier>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/(?P<index>[\d]+)/','image.rotateimage'),
  (r'^data/fetchimage/(?P<supplier>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/(?P<index>[\d]+)/','image.fetchimage'),
  )

