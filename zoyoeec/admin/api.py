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
from core import error, retailtype, retail, userapi, page, zoyoeforms
from model import *

# Config the website 
#
#
def __fetchinfo(k,content,type):
  if(type == "private"):
    siteinfo = retailtype.getSiteInfo()
    keys = siteinfo.__dict__
    properties = siteinfo.properties()
    return properties.get(k)
  else:
    line = ShopInfo.all().filter("name =",k).get()
    if not line:
      return None
    else:
      return line.content

def __feedinfo(k,content,type):
  if(type == "private"):
    __configsite(k,content)
  else:
    line = ShopInfo.all().filter("name =",k).get()
    if not line:
      line = ShopInfo(name=k,content=content,type=type)
      line.put()
    else:
      line.content = content
      line.put()


def __configsite(attr,content):
  siteinfo = retailtype.getSiteInfo()
  keys = siteinfo.__dict__
  properties = siteinfo.properties()
  if (attr in properties):
     model = properties.get(attr)
     if isinstance(model, db.StringProperty):
       setattr(siteinfo,attr,content)
     elif isinstance(model,db.BooleanProperty):
       setattr(siteinfo,attr,(False,True)[content == "True"])
     elif isinstance(model,db.TextProperty):
       setattr(siteinfo,attr,content)
     else: 
       pass
  siteinfo.put()

@userapi.authority_config
def addconfig(request):
  rf = zoyoeforms.AlterConfig(request.POST)
  if rf.is_valid():
      title = rf.cleaned_data['title']
      type = rf.cleaned_data['type']
      content = rf.cleaned_data['content']
      __feedinfo(title,content,type])
      return error.jsonReply(True, __fetchinfo(title))
  else:
      return error.jsonReply(True, zoyoeforms.fetchError(rf))
  return response

@userapi.authority_config
def removeconfig(request):
  if ("title" in request.POST):
    line = ShopInfo.all().filter("name =",request.POST['title']).get()
    if line:
      line.delete()
      return error.jsonReply(True, __fetchinfo(request.POST['title']))
    else:
      return error.jsonReply(Flase, "config item not found")
  else:
    return error.jsonReply(Flase, "config item not found")

#FIXME: not good now
@zuser.authority_item
def addsupplier(request):
  supdata = {'store':order.supplier,
      'category':{'other':{'name':'misc','children':{}}}}
  supplier = Supplier(name = order.supplier,data=json.dumps(supdata['category']))
  supplier.put()



#### End website config ####

