import django.core.handlers.wsgi
import ebayapi,zuser,retailtype
import datetime,urllib2,httplib,random,json
from django import forms
from django.core.context_processors import csrf
from google.appengine.ext import db,blobstore,deferred
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.runtime.apiproxy_errors import RequestTooLargeError 
from urllib import urlencode
from ebay import ebay_view_prefix,ebay_ajax_prefix,getinactivelist,getactivelist, getEbayInfo, sync,relist, format
from order import *
from error import *
from page import *
from retail import getSupplierFromEbayInfo,Supplier,Item,ShopInfo,ImageData,formatName

# ####
# return ZoyoeSuccess if images are added
# ####
@csrf_exempt
@zuser.authority_item
@ebay_view_prefix
def addimages(request,supplier):
  file = request.FILES['files[]'].read()
  name = request.FILES['files[]'].name.split(".")
  name.pop()
  rid = ".".join(name)
  item = createDefaultItem(rid,supplier)
  picture = quickrescale(file, 600)
  idx = 0
  img = item.getImage(idx)
  if img:
    img.image = picture
    img.small = createsc(img.image)
    img.put()
  else:
    img = ImageData(image=picture,name=item.name,parent=item,idx=idx) 
    img.url = "http://" + request.META['HTTP_HOST'] + "/admin/fetchimage/" + item.parent().name + "/" + str(item.key().id()) + "/" + str(idx)
    img.small = createsc(img.image)
    img.put()
    del picture
    item.galleryurl = img.url
    item.put()
  return HttpResponse("ok")

# Ebay sync functions

@zuser.authority_ebay
@ebay_view_prefix
def exporttoebay(request,shop,key):
  __register_admin_action(request,"ebayexport",shop+"/"+key)
  token = ebay.getToken(request)
  item = Item.get_by_id(int(key),parent = getSupplier(shop))
  if item:
    if (item.ebayid and (item.ebayid != '0')):
      info = ebay.getEbayInfo(request)
      rslt = sync(info,item)
      return HttpResponse(rslt,mimetype="text/xml")
    rslt = ebayapi.api.AddItem(token,item)
    xml_doc = etree.parse(StringIO(rslt))
    ack = xml_doc.xpath("//xs:Ack",
      namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
    if(not 'Failure' in ack.text):
      itemid = xml_doc.xpath("//xs:ItemID",
        namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
      item.ebayid = itemid
      item.put()
    return HttpResponse(rslt,mimetype="text/xml")

@zuser.authority_ebay
@ebay_view_prefix
def relisttoebay(request,shop,key):
  __register_admin_action(request,"ebayrelist",shop+"/"+key)
  info = ebay.getEbayInfo(request)
  item = Item.get_by_id(int(key),parent = Supplier.getSupplierByName(shop))
  if item:
    if (item.ebayid and (item.ebayid != '0')):
      rslt,item = relist(info,item)
      return rslt
  return (returnError("item not find or not exists in ebay"))

@ebay_ajax_prefix
def importfromebay(request,ebayinfo,itemid):
  (rslt,item) = format(ebayinfo,itemid)
  if item:
    __register_admin_action(request,"ebaydepoly",item.parent().name+"/"+str(item.key().id()))
    return rslt
  else:
    return rslt
 

@ebay_view_prefix
def syncwithebay(request,shop,key):
  __register_admin_action(request,"ebayexport",shop+"/"+key)
  info = ebay.getEbayInfo(request)
  item = Item.get_by_id(int(key),parent = Supplier.getSupplierByName(shop))
  if item:
    rslt = sync(info,item)
    return rslt


