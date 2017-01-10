import django.core.handlers.wsgi
import datetime,urllib2,httplib,random,json
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader,Context,RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.cache import never_cache
from google.appengine.ext import db,blobstore,deferred
from google.appengine.api import users,images
from google.appengine.runtime.apiproxy_errors import RequestTooLargeError 
from core import error, userapi, page, zoyoeforms, dbtype
from model import *

# Config the website 
#
#
def __fetchinfo(k,cate):
  if(cate == "private"):
    siteinfo = dbtype.getSiteInfo()
    keys = siteinfo.__dict__
    properties = siteinfo.properties()
    return getattr(siteinfo,k)
  else:
    line = dbtype.ShopInfo.all().filter("name =",k).get()
    if not line:
      return None
    else:
      return line.content

# json info
def __json_shopinfo(k,type,content):
  info = {}
  info['title'] = k
  info['category'] = type 
  info['content'] = content
  return info

def __feedinfo(k,content,type):
  if(type == "private"):
    ret = __configsite(k,content)
    if ret:
      return __json_shopinfo(k,type,content)
    else:
      return None
  else:
    line = dbtype.ShopInfo.all().filter("name =",k).get()
    if not line:
      line = dbtype.ShopInfo(name=k,content=content,type=type)
      line.put()
    else:
      line.content = content
      line.put()
    return __json_shopinfo(k,type,content)

def __json_supplierinfo(supplier):
  info = {}
  info['name'] = supplier.name
  info['data'] = json.loads(supplier.data)
  info['lock'] = supplier.islocked
  return info



def __configsite(attr,content):
  siteinfo = dbtype.getSiteInfo()
  keys = siteinfo.__dict__
  properties = siteinfo.properties()
  if (attr in properties):
     model = properties.get(attr)
     if isinstance(model, db.StringProperty):
       setattr(siteinfo,attr,content)
     elif isinstance(model,db.BooleanProperty):
       setattr(siteinfo,attr,(False,True)[content in ["True","true"]])
     elif isinstance(model,db.TextProperty):
       setattr(siteinfo,attr,content)
     else: 
       return None
  siteinfo.put()
  return siteinfo

@userapi.authority_config
def configapi(request):
  rf = zoyoeforms.Config(request.POST)
  if rf.is_valid():
    title = rf.cleaned_data['title']
    type = rf.cleaned_data['type']
    content = rf.cleaned_data['content']
    command = rf.cleaned_data['command']
    if (command == 'alter'):
      ret = __feedinfo(title,content,type)
      if ret:
        return error.jsonReply(True, ret)
      else:
        er = zoyoeforms.constructError("title","item " + title + " not found")
        return error.jsonReply(False, er)
    if (command == 'add'):
      ret = __feedinfo(title,content,type)
      if ret:
        return error.jsonReply(True, ret)
      else:
        er = zoyoeforms.constructError("title","item " + title + " not valid")
        return error.jsonReply(False, er)
    if (command == 'delete'):
      if ("title" in request.POST):
        line = dbtype.ShopInfo.all().filter("name =",request.POST['title']).get()
        if line:
          line.delete()
          return error.jsonReply(True, "")
      else:
        er = zoyoeforms.constructError("title","item " + title + " not found")
        return error.jsonReply(False, er)
    er = zoyoeforms.constructError("command","unknown command " + command)
    return error.jsonReply(False, er)
  else:
    return error.jsonReply(False, zoyoeforms.fetchError(rf))

@userapi.authority_item
def supplierapi(request):
  rf = zoyoeforms.Supplier(request.POST)
  if rf.is_valid():
    name = rf.cleaned_data['name']
    data = rf.cleaned_data['data']
    lock = rf.cleaned_data['lock']
    command = rf.cleaned_data['command']
    if (command == 'alter'):
      supplier = Supplier.getSupplierByName(name)
      if supplier:
        try:
          supplier.name = name
          supplier.lock = lock
          supplier.data = json.dumps(json.loads(data))
          supplier.put()
          return error.jsonReply(True,__json_supplierinfo(supplier))
        except:
          er = zoyoeforms.constructError("malformed data")
    if (command == 'delete'):
      if (name == getSiteInfo().mainshop):
        er = zoyoeforms.constructError("title","main shop " + name + " can not been deleted")
        return error.jsonReply(False, er)
      else:
        delete(supplier)
        return error.jsonReply(True, "")
    if (command == 'add'):
      supplier = dbtype.createSupplier(name,data,lock)
      if supplier:
        return error.jsonReply(True,__json_supplierinfo(supplier))
      else:
        er = zoyoeforms.constructError("title","main shop " + name + " can not been created")
        return error.jsonReply(False, er)
    er = zoyoeforms.constructError("command","unknown command " + command)
    return error.jsonReply(False, er)
  else:
    return error.jsonReply(False, zoyoeforms.fetchError(rf))


@userapi.authority_item
def addsupplier(request):
  supdata = {'store':order.supplier,
      'category':{'other':{'name':'misc','children':{}}}}
  supplier = Supplier(name = order.supplier,data=json.dumps(supdata['category']))
  supplier.put()



#### End website config ####

