from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import ebayapi

urlpatterns = patterns('',
  (r'^$', 'core.main.main'),
  (r'^workspace/$', 'core.main.workspace'),
  (r'^createworkspace/$', 'core.main.createworkspace'),
  (r'^search/$', 'retail.searchjson'),
  (r'^match/$', 'retail.matchjson'),
  (r'^token/$', 'ebay.token'),
  (r'^format/(?P<itemid>\d*)/', 'ebayapi.ebay.importfromebay'),
  (r'^relist/(?P<itemid>\d*)/', 'ebayapi.ebay.importfromebay'),
  (r'^item/(?P<shop>[a-zA-Z\d_\s]+)/(?P<key>[a-zA-Z\d]+)/$','main.item'),


####
#
# root of admin
#
####
  (r'^admin/$', 'core.main.admin'),

####
#
# site user login/out/register
#
####
  (r'^login/$', 'core.main.login'),
  (r'^logout/$', 'core.main.logout'),
  (r'^register/$', 'core.main.register'),

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

## Admin Section
# browsing stuff
  (r'^admin/item/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/$','admin.view.item'),
  (r'^admin/additem/$','admin.view.additem'),
  (r'^admin/deploy/$', 'admin.view.deploy'),
  (r'^admin/relist/$', 'admin.view.relistlist'),
  (r'^admin/actionhistory/$','admin.view.actionhistory'),
  (r'^admin/saveitem/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/$','admin.view.saveitem'),
  (r'^admin/deleteitem/(?P<shop>[a-zA-Z\d_]+)/(?P<key>[a-zA-Z\d]+)/$','admin.view.deleteitem'),
  (r'^admin/ebayitems/(?P<shop>[a-zA-Z\d_]+)/', 'admin.view.ebayitems'),
  (r'^admin/unpublisheditems/(?P<shop>[a-zA-Z\d_]+)/', 'admin.view.unpublisheditems'),
  (r'^admin/items/(?P<supplier>[a-zA-Z\d_]+)/$', 'admin.view.supplieritems'),
  (r'^admin/items/(?P<supplier>[a-zA-Z\d_]+)/(?P<category>[a-zA-Z\d]+)/', 'admin.view.items'),

# Image based 
  (r'^admin/image/','image.urls'),

# Admin site config view
  (r'^admin/feedinfo/$', 'admin.setupinfo'),
  (r'^admin/addconfig/$', 'admin.addconfig'),

# config views
  (r'^admin/config/preference/$', 'admin.view.preference'),
  (r'^admin/config/ebay/$', 'admin.view.ebayconfig'),

####
#
# ebay component
#
####

  url(r'^ebay/',include('ebayapi.urls')),

####
#
# end of admin section
#
####

# resource stuff
  (r'^image/item/(?P<itemid>[a-zA-Z\d_\-\.]+)/$', 'admin.fetchimagebyrid'),

# json stuff
  (r'^json/categories/$', 'jsonapi.categories'),
  (r'^json/items/(?P<category>[a-zA-Z\d]+)/$', 'jsonapi.items'),
  (r'^json/item/(?P<itemid>[a-zA-Z\d\-\.]+)/$', 'jsonapi.item'),
  (r'^ebayjson/$', 'main.ebayjson'),

# rest api
  (r'^retail/get/','retail.get'),
  (r'^rest/cart/$', 'retail.cartinfo'),

####
#
# FIXME:
# DEBUG: A good debug framework is needed for data migration
#
####

# (r'^namespace/$', 'main.namespace'),
  (r'^admin/scanitems/$', 'admin.scanitems'),
  (r'^admin/checkurl/$', 'admin.checkurl'),
  (r'^admin/checkimages/$', 'admin.replaceimage'),
  (r'^admin/checkitems/$', 'retailtype.checkrid'),
  (r'^admin/checkindex/$', 'retailtype.resetIndex'),
  (r'^admin/cleanitems/$', 'admin.cleanitems'),
  (r'^admin/fixsupplier/$', 'admin.fixsupplier'),
)
