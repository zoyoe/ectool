import django.core.handlers.wsgi
from django.core.context_processors import csrf
from django.template import loader,Context,RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from ebaysdk import finding
from ebaysdk.exception import ConnectionError
from error import *
import ebay, random
import urllib2,httplib
import requests,json,datetime
from google.appengine.ext import db
from google.appengine.api import search


#####
#  data = {'id': XX,'email': XX,'logo':XX,
#    'categories': categories}
#
#
class SiteInfo(db.Model):
  logo = db.BlobProperty(default=None)
  mainshop = db.StringProperty(default=None)
  analytics = db.StringProperty(default=None)
  published = db.BooleanProperty()
  trial = db.BooleanProperty()
  template = db.StringProperty(default=None)

def siteinfo():
  site = SiteInfo.all().get()
  stories = {}
  if site:
    supplier = getSupplier(site.mainshop) 
    stories[supplier.name] = json.loads(supplier.data)
  return stories

def formatRID(name):
  return name.replace(" ", "_").upper().encode('ascii','ignore')

class Supplier(db.Model):
  name = db.StringProperty(required=True)
  data = db.TextProperty(default='{}')
  def saveItem(self,iteminfo,overwrite=True):
    item = getItem(iteminfo['refid'])
    if (item):
      item.name = iteminfo['name']
      item.price = iteminfo['price']
      if "ebaycategory" in iteminfo:
        item.ebaycategory = iteminfo['ebaycategory']
      if overwrite:
        item.refid = formatRID(iteminfo['refid'])
        item.galleryurl = iteminfo['galleryurl']
        item.currency = 'AUD'
        item.infourl = iteminfo['infourl']
        item.category = iteminfo['category']
        item.category2 = iteminfo['sndcategory']
        item.description = iteminfo['description']
        item.ebayid = iteminfo['ebayid']
        item.specification = iteminfo['specification']
      item.put()
      indexItem(item)
      return item
    else:
      item = Item(refid = formatRID(iteminfo['refid'])
        ,name = iteminfo['name']
        ,price = iteminfo['price']
        ,cost = iteminfo['cost']
        ,galleryurl = iteminfo['galleryurl']
        ,currency = 'AUD'
        ,infourl = iteminfo['infourl']
        ,category = iteminfo['category']
        ,category2 = iteminfo['sndcategory']
        ,description = iteminfo['description']
        ,specification = iteminfo['specification']
        ,ebayid = iteminfo['ebayid']
        ,parent = self
       )
      if "ebaycategory" in iteminfo:
        item.ebaycategory = iteminfo['ebaycategory']
      item.put()
      indexItem(item)
      return item
  def getItems(self):
    return Item.all().ancestor(self)
  def getCategoryItems(self,category):
    return Item.all().ancestor(self).filter("category =",category)
  def getCategoryItems(self,category):
    return Item.all().ancestor(self).filter("category2 =",category)
  def getItem(self,key):
    return Item.get_by_id(key,parent=self)
  def getStat(self,category=None):
    if category:
      return Item.all().ancestor(self).filter("category =",category).count()
    else:
      return Item.all().ancestor(self).count()
  def getEbayStat(self):
    return Item.all().ancestor(self).filter("ebayid !=",None).filter("ebayid !=","").count()
  def getEbayItems(self):
    return Item.all().ancestor(self).filter("ebayid !=",None).filter("ebayid !=","")
  def getUnpublishedItems(self):
    return Item.all().ancestor(self).filter("ebayid =",None)



def getCategoryItems(category):
  return Item.all().filter("category =",category)


class ImageData(db.Model):
  image = db.BlobProperty(default=None)
  name = db.StringProperty(required=True) 
  idx = db.IntegerProperty(required=True)
  url = db.StringProperty(default=None)

class Item(db.Model):
  refid = db.StringProperty(required=True)
  name = db.StringProperty(required=True)
  galleryurl = db.StringProperty(required=True)
  price = db.FloatProperty()
  cost = db.FloatProperty()
  currency = db.StringProperty(required=True)
  infourl = db.StringProperty(required=True)
  category = db.StringProperty(default='1')
  category2 = db.StringProperty(default='1')
  description = db.TextProperty(default="")
  specification = db.TextProperty(default="")
  ebayid = db.StringProperty(default="")
  picture = db.BlobProperty(default=None)
  ebaycategory = db.TextProperty(default=None)
  def getImage(self,idx):
    return ImageData.all().ancestor(self).filter("idx =",idx).get()
  def getImages(self):
    return ImageData.all().ancestor(self).order("idx")
  def getSpecification(self):
    try:
      obj = json.loads(self.specification)
      return obj
    except:
      return {}

def createDefaultItem(refid,suppliername="Anonymous"):
  item = getItem(refid)
  if item:
    return item
  else:
    iteminfo = {
      'refid':refid,
      'name':"not provided",
      'price':0.0,
      'cost':0.0,
      'galleryurl':'/static/res/picnotfound.jpg',
      'infourl':'#',
      'category':'other',
      'sndcategory':'other',
      'ebayid': None,
      'specification':'{}',
      'description':'No extra description provided'
    }
    supplier = getSupplier(suppliername)
    if supplier:
      return supplier.saveItem(iteminfo)
    else:
      supplier = Supplier(name=suppliername)
      supplier.put()
      return supplier.saveItem(iteminfo)


class ShopInfo(db.Model):
  name = db.StringProperty(required=True)
  content = db.TextProperty(required=True)
  type = db.StringProperty(default="")

def getItem(rid):
  formatrid = formatRID(rid)
  supplier = db.GqlQuery("SELECT * FROM Item WHERE refid = :1",formatrid)
  return supplier.get()

def getSupplier(sname):
  suppliers = db.GqlQuery("SELECT * FROM Supplier WHERE name = :1",sname)
  return suppliers.get()

def ridcode(iid):
  return iid;

def deleteItemIndex(item):
  index = search.Index(name="itemindex")
  index.delete(item.refid)

def indexItem(item):
  try:
    document = search.Document(
      doc_id = item.refid,
      fields=[
       search.TextField(name='title', value=item.name),
       search.TextField(name='description', value=item.description + " " + item.specification),
       ])
    index = search.Index(name="itemindex")
    index.put(document)
    return document
  except search.Error:
    return None

def checkrid(request):
  items = Item.all()
  for item in items:
    item.refid = formatRID(item.refid)
    item.put()
  return HttpResponse("OK")

def resetIndex(request):
  items = Item.all()
  for item in items:
    indexItem(item)
  return HttpResponse("OK")
    


