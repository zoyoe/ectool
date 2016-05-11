urlpatterns = patterns('image',
  (r'^addimage/','admin.addimage'),
  (r'^addimages/(?P<supplier>[a-zA-Z\d_]+)/$','admin.addimages'), ## Is this still usefull ?
  (r'^uploadimages/$','admin.view.uploadimages'),
  (r'^uploadimage/(?P<supplier>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/(?P<index>[\d]+)/','admin.uploadimage'),
  (r'^rotateimage/(?P<supplier>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/(?P<index>[\d]+)/','admin.rotateimage'),
  (r'^fetchimage/(?P<supplier>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/(?P<index>[\d]+)/','admin.fetchimage'),

