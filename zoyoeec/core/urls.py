from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('core',
  (r'^$', 'main.main'),
  (r'^workspace/$', 'main.workspace'),
  (r'^login/$', 'main.login'),
  (r'^logout/$', 'main.logout'),
  (r'^register/$', 'main.register'),
  (r'^find/$', 'main.find'),
  (r'^auth/$', 'ebay.auth'),
  (r'^logoutebay/$', 'ebay.logoutebay'),
  (r'^search/$', 'retail.searchjson'),
  (r'^match/$', 'retail.matchjson'),
  (r'^authsuccess/$', 'ebay.authsuccess'),
  (r'^authfail/$', 'ebay.authfail'),
  (r'^token/$', 'ebay.token'),
  (r'^format/(?P<itemid>\d*)/', 'admin.importfromebay'),
  (r'^relist/(?P<itemid>\d*)/', 'admin.importfromebay'),
  (r'^item/(?P<shop>[a-zA-Z\d_\s]+)/(?P<key>[a-zA-Z\d]+)/$','main.item'),

# items view pages
  (r'^items/(?P<shop>[a-zA-Z\d_]+)/(?P<category>[a-zA-Z\d]+)/', 'main.items'),
  (r'^items/search/', 'retail.searchview'),

# some user specific pages
  (r'^user/viewhistory/','record.getItemHistoryResponse'),
  (r'^user/receipts/','retail.receipts'),

# not sure how to split the admin stuff
  (r'^retail/receiptview/','retail.receiptview'),
  (r'^retail/add/','retail.add'),
  (r'^retail/remove/(?P<item>[a-zA-Z\d_\-]+)/','retail.remove'),
  (r'^retail/checkoutcart/','retail.checkoutcart'),
  (r'^retail/sendpaypalinvoice/(?P<key>[a-zA-Z\d]+)/','retail.sendpaypalinvoice'),
  (r'^retail/expresspaypal/(?P<key>[a-zA-Z\d]+)/','retail.expresspaypal'),
  (r'^retail/receipt/(?P<key>[a-zA-Z\d]+)/','retail.receipt'),
  (r'^retail/editreceipt/(?P<key>[a-zA-Z\d]+)/','retail.editreceipt'),
  (r'^retail/deletereceipt/(?P<key>[a-zA-Z\d]+)/','retail.deletereceipt'),
  (r'^retail/checkout/(?P<key>[a-zA-Z\d]+)/','retail.checkout'),
  (r'^pos/','main.pos'),

#shopping cart and billinginfo are combined here
  (r'^shoppingcart/','retail.billinginfo'),
  (r'^receipts/','main.receipts'),
  (r'^paypalpdt/','retail.paypalpdt'),
  (r'^paypal/accept/','retail.paypalaccept'),
  (r'^order/importpdf/','main.pdforder'),
  (r'^order/importcsv/','main.csvorder'),
  (r'^order/saveorder/','order.saveorder'),
  (r'^order/modifyorder/','order.modifyorder'),
  (r'^order/orderview/','order.orderview'),
  (r'^order/deploy/','order.deploy'),
  (r'^order/delete/','order.deleteorder'),
  (r'^orders/ebay/','ebay.ebayorders'),
  (r'^orders/ebayajax/','ebay.ebayordersajax'),
  (r'^orders/','order.orders'),

# admin stuff
  (r'^admin/item/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/$','admin.item'),
  (r'^admin/additem/$','admin.additem'),
  (r'^admin/deploy/$', 'admin.deploy'),
  (r'^admin/relist/$', 'admin.relistlist'),
  (r'^admin/actionhistory/$','admin.actionhistory'),
  (r'^admin/saveitem/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/$','admin.saveitem'),
  (r'^admin/deleteitem/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/$','admin.deleteitem'),
  (r'^admin/itemimage/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/$','admin.itemimage'),
  (r'^admin/uploadimages/$','admin.uploadimages'),
  (r'^admin/items/(?P<shop>[a-zA-Z\d_]+)/(?P<category>[a-zA-Z\d]+)/', 'admin.items'),
  (r'^admin/ebayitems/(?P<shop>[a-zA-Z\d_]+)/', 'admin.ebayitems'),
  (r'^admin/unpublisheditems/(?P<shop>[a-zA-Z\d_]+)/', 'admin.unpublisheditems'),
  (r'^admin/items/(?P<shop>[a-zA-Z\d_]+)/$', 'admin.supplieritems'),
  (r'^admin/addimage/','admin.addimage'),
  (r'^admin/addimages/(?P<supplier>[a-zA-Z\d_]+)/$','admin.addimages'),
  (r'^admin/blobimage/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/(?P<index>[\d]+)/','admin.blobimage'),
  (r'^admin/rotateimage/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/(?P<index>[\d]+)/','admin.rotateimage'),
  (r'^admin/fetchimage/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/(?P<index>[\d]+)/','admin.fetchimage'),
  (r'^admin/exporttoebay/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/','admin.exporttoebay'),
  (r'^admin/syncwithebay/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/','admin.syncwithebay'),
  (r'^admin/relisttoebay/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/','admin.relisttoebay'),
  (r'^admin/categories/$', 'ebay.fetchcategory'),
  (r'^admin/$', 'main.admin'),

  (r'^admin/feedinfo/$', 'admin.setupinfo'),
  (r'^admin/addconfig/$', 'admin.addconfig'),
  (r'^admin/config/preference/$', 'admin.preference'),
  (r'^admin/config/ebay/$', 'admin.ebayconfig'),

  (r'^json/categories/$', 'jsonapi.categories'),
  (r'^json/items/(?P<category>[a-zA-Z\d]+)/$', 'jsonapi.items'),
  (r'^json/item/(?P<itemid>[a-zA-Z\d\-\.]+)/$', 'jsonapi.item'),
  (r'^ebayjson/$', 'main.ebayjson'),

# rest api
  (r'^retail/get/','retail.get'),
  (r'^rest/cart/$', 'retail.cartinfo'),
# debug
# (r'^namespace/$', 'main.namespace'),
  (r'^admin/scanitems/$', 'admin.scanitems'),
  (r'^admin/checkurl/$', 'admin.checkurl'),
  (r'^admin/checkimages/$', 'admin.replaceimage'),
  (r'^admin/checkitems/$', 'retailtype.checkrid'),
  (r'^admin/checkindex/$', 'retailtype.resetIndex'),
  (r'^admin/cleanitems/$', 'admin.cleanitems'),
)
