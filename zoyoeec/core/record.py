import django.core.handlers.wsgi
import random,json
import userapi,error,dbtype
from django.template import loader,Context,RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response

def getItemResponse(request,item,stories):
  if item:
    dict = {'ITEM':item,'STORIES':stories}
    context = Context(dict)
    recordItemHistory(request,item)
    tpath = dbtype.getSiteInfo().getTemplate("retailitem.html");
    return (render_to_response(tpath,context,context_instance=RequestContext(request)))
  else:
    return error.retailError(request,"item not found")

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
      item = dbtype.Item.getItemByRID(rid)
      if item:
        rslt.append(item)
  return rslt

def getItemHistoryResponse(request):
  itemrefs = getItemHistory(request)
  items = []
  if (itemrefs != None):
    for ref in itemrefs:
      items.append(dbtype.Item.getItemByRID(ref))
    stories = dbtype.getCategoriesInfo()
    lvl1 = "Viewing History"
    dict = {'SHOP':'Items you recently viewed','STORIES':stories,'PATH':lvl1,'CATEGORY':""}
    dict['sellitems'] = items
    context = Context(dict)
    temp_path = dbtype.currentSite().getTemplate("products.html");
    return (render_to_response(temp_path,context,context_instance=RequestContext(request)))
  else:
    return error.UserError(request,"Your have not signed in")
  


