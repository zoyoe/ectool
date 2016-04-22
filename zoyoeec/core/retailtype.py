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



class SiteInfo(db.Model):

  """ site logo, it should be a must if site is published
      but we do not enforce it at the moment
  """
  logo = db.BlobProperty(default=None)

  """ the mainshop is a pseudo supplier that
      we used to store the information of categories
  """
  mainshop = db.StringProperty(default=None)

  """ google analytic code
  """
  analytics = db.StringProperty(default=None)

  """ whether this site has been published on www.zoyoe.com
  """
  published = db.BooleanProperty(default=False)

  """ whether the retail part of this site requires login
  """
  requirelogin = db.BooleanProperty(default=False)

  type = db.StringProperty()
  siteinfo = db.TextProperty(default=None)
  ebayinfo = db.TextProperty(default=None)

  """ paypal account used to receive funds for this site
  """
  paypal = db.TextProperty(default=None)

  """ templatename for the retail part of this site
  """
  template = db.StringProperty(default=None)

  """ return the template path regarding certain file name
  """
  def gettemplate(self,name):
    if self.template:
      return self.template + "/" + name
    else:
      return "default/" + name 

  def setebayinfo(ebayinfo):
    self.ebayinfo = ebayinfo
    self.put()

def currentSite():
  return SiteInfo.all().get()

def getSiteInfo():
  site = SiteInfo.all().get()
  if (site):
    return site
  else:
    site = SiteInfo()
    return site

def getCategoriesInfo():
  site = getSiteInfo()
  stories = {}
  if site:
    supplier = getSupplier(site.mainshop) 
    if(supplier):
      stories[supplier.name] = json.loads(supplier.data)
  return stories

def formatRID(name):
  return name.replace(" ", "_").upper().encode('ascii','ignore')

class Supplier(db.Model):
  """ data is a json object.
  data = {'id': XX,'email': XX,'logo':XX,
    'categories': categories}
  """
  data = db.TextProperty(default='{}')
  name = db.StringProperty(required=True)
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
  def getSndCategoryItems(self,category):
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
  small = db.BlobProperty(default=None)
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
  disable = db.BooleanProperty(default=True)
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
  def payment(self):
    site = SiteInfo.all().get()
    return site.paypal
    

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


# Follwing are helper functions

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


# Schema updating functions

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
    


