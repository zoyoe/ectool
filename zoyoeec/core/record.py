import django.core.handlers.wsgi
from django.template import loader,Context,RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
from ebay import ebay_view_prefix,getactivelist, getEbayInfo
from retail import getSupplier,saveSupplier,getSupplierFromEbayInfo,Supplier,Item,SiteInfo
import random,json
from retailtype import siteinfo, getCategoryItems, getItem
from google.appengine.ext import db
from google.appengine.api import users
from error import *
import zuser

def getItemResponse(request,item,stories):
  if item:
    dict = {'ITEM':item,'STORIES':stories}
    context = Context(dict)
    recordItemHistory(request,item)
    return (render_to_response("retailitem.html",context,context_instance=RequestContext(request)))
  else:
    return retailError(request,"item not found")

def recordItemHistory(request,item):
  user = zuser.getCurrentUser()
  if user:
    history = user.history
    if not history:
      history = "{}"
    history = json.loads(history)
    if 'items' in history:
      items = history['items']
    else:
      items = []
    if item.refid in items:
      items.remove(item.refid)
    items = [item.refid] + items
    if (len(items) > 30):
      items.pop()
    history['items'] = items
    user.history = json.dumps(history)
    user.put()

def getItemHistory(request):
  user = zuser.getCurrentUser()
  if user:
    history = user.history
    if not history:
      history = "{}"
    history = json.loads(history)
    if 'items' in history:
      items = history['items']
    else:
      items = []
    return items
  else:
    return None


def getItemHistoryResponse(request):
  itemrefs = getItemHistory(request)
  items = []
  if (itemrefs != None):
    for ref in itemrefs:
      items.append(getItem(ref))
    stories = siteinfo()
    lvl1 = "Viewing History"
    dict = {'SHOP':'Items you recently viewed','STORIES':stories,'PATH':lvl1,'CATEGORY':""}
    dict['sellitems'] = items
    context = Context(dict)
    return (render_to_response("retail.html",context,context_instance=RequestContext(request)))
  else:
    return userError(request,"Your have not signed in")
  


