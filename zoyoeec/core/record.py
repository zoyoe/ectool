import django.core.handlers.wsgi
import random,json
import userapi 
from django.template import loader,Context,RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
from dbtype import getCategoriesInfo, Item
from google.appengine.ext import db
from google.appengine.api import users
from error import *

def getItemResponse(request,item,stories):
  if item:
    dict = {'ITEM':item,'STORIES':stories}
    context = Context(dict)
    recordItemHistory(request,item)
    tpath = getSiteInfo().getTemplate("retailitem.html");
    return (render_to_response(tpath,context,context_instance=RequestContext(request)))
  else:
    return retailError(request,"item not found")

def recordItemHistory(request,item):
  user = userapi.getCurrentUser(request)
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
    if (len(items) > 10):
      items.pop()
    history['items'] = items
    user.history = json.dumps(history)
    user.put()

def getItemHistory(request):
  user = userapi.getCurrentUser(request)
  rslt = []
  if user:
    history = user.history
    if not history:
      history = "{}"
    history = json.loads(history)
    if 'items' in history:
      items = history['items']
    else:
      items = []
    for rid in items:
      item = Item.getItemByRID(rid)
      if item:
        rslt.append(item)
  return rslt

def getItemHistoryResponse(request):
  itemrefs = getItemHistory(request)
  items = []
  if (itemrefs != None):
    for ref in itemrefs:
      items.append(Item.getItemByRID(ref))
    stories = getCategoriesInfo()
    lvl1 = "Viewing History"
    dict = {'SHOP':'Items you recently viewed','STORIES':stories,'PATH':lvl1,'CATEGORY':""}
    dict['sellitems'] = items
    context = Context(dict)
    temp_path = currentSite().getTemplate("products.html");
    return (render_to_response(temp_path,context,context_instance=RequestContext(request)))
  else:
    return userError(request,"Your have not signed in")
  


