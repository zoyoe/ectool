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
from core import error, retailtype, retail, userapi, page
from model import *

application = django.core.handlers.wsgi.WSGIHandler()


#  This is a helper function for standard paged query.
#  It will fill context needed for paging
#
def pageItems(query,dict,url,request):
  myPagedQuery = page.PagedQuery(query,48)
  dict['queryurlprev'] = "#" 
  dict['queryurlnext'] = "#" 
  total = myPagedQuery.page_count()
  dict['pages'] = range(1,total+1)
  idx = 0
  if ('page' in request.GET):
    idx = int(request.GET['page'])
    items = myPagedQuery.fetch_page(int(request.GET['page']))
  else:
    items = myPagedQuery.fetch_page()
  if (idx > 1):
    dict['queryurlprev'] = url + "?page="+str(idx-1)
  if (idx <= total):
    dict['queryurlnext'] = url +"?page="+str(idx+1)
  dict['queryurl'] = url
  return items


# Display the action history 
#
@userapi.authority_config
def actionhistory(request):
  dict = {}
  dict['actions'] = pageItems(AdminAction.all().order("-date"),
      dict,"/admin/actionhistory/",request)
  context = Context(dict)
  return (render_to_response("./admin/history.html",context,context_instance=RequestContext(request)))


#####
#   
#   Various views for items.
#
####

@userapi.authority_item
def unpublisheditems(request,suppliername):
  supplier = Supplier.getSupplierByName(suppliername)
  dict = {'SHOP':suppliername,'ITEM_WIDTH':'200'}
  if (supplier):
    dict['sellitems'] = pageItems(supplier.getUnpublishedItems(),dict,
        "/admin/items/"+suppliername+"/",request)
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))
  else:
    dict['sellitems'] = []
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))


@userapi.authority_item
def ebayitems(request,shop):
  supplier = Supplier.getSupplierByName(shop)
  dict = {'SHOP':shop,'ITEM_WIDTH':'200'}
  if (supplier):
    dict['sellitems'] = supplier.getEbayItems()
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))
  else:
    dict['sellitems'] = []
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))


@userapi.authority_item
def items(request,suppliername,category):
  supplier = Supplier.getSupplier(suppliername)
  suppliers = Supplier.all()
  stories = {}
  lvl1 = "Category"
  lvl2 = "Gallery"
  for supply in suppliers:
    stories[supply.name] = json.loads(supply.data)
    if (supply.name == suppliername):
      for c in stories[supply.name]:
        if (category in stories[supply.name][c]['children']):
          lvl1 = stories[supply.name][c]['name']
          lvl2 = stories[supply.name][c]['children'][category]['name']
  dict = {'SHOP':suppliername,'ITEM_WIDTH':'200','STORIES':stories,'PATH':lvl1,'CATEGORY':lvl2}
  if (supplier):
    dict['sellitems'] = pageItems(supplier.getCategoryItems(category),
        dict,"/admin/items/"+suppliername+"/" + category + "/",request)
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))
  else:
    dict['sellitems'] = []
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))

@userapi.authority_item
def supplieritems(request,suppliername): 
  supplier = Supplier.getSupplierByName(suppliername)
  suppliers = [supplier]
  stories = {}
  lvl1 = "Category"
  lvl2 = "Gallery"
  for supply in suppliers:
    stories[supply.name] = json.loads(supply.data)
  dict = {'SHOP':suppliername,'ITEM_WIDTH':'200','STORIES':stories,'PATH':'All','CATEGORY':''}
  if (supplier):
    dict['sellitems'] = pageItems(supplier.getItems(),
        dict,"/admin/items/" + suppliername + "/",request)
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))
  else:
    dict['sellitems'] = []
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))



#### End Section 


#### Section: Item manipulation views.

@userapi.authority_item
def additem(request):
  rid = request.GET['rid']
  item = retailtype.createDefaultItem(rid)
  response =  HttpResponseRedirect('/admin/item/'+ item.parent().name + '/' + str(item.key().id()) +"/")
  return response
  

@userapi.authority_item
def deleteitem(request,shop,key):
  item = Item.get_by_id(int(key),parent = Supplier.getSupplierByName(shop))
  if item:
    item.deleteIndex()
    item.delete()
  return HttpResponseRedirect('/admin/items/'+shop)

@userapi.authority_item
def item(request,shop,key):
  stories = retailtype.getCategoriesInfo()
  item = Item.get_by_id(int(key),parent = Supplier.getSupplierByName(shop))
  if item:
    upload_url = '/admin/blobimage/'+ shop + "/" + key +"/0/"
    upload_url1 = '/admin/blobimage/'+ shop + "/" + key +"/1/"
    upload_url2 = '/admin/blobimage/'+ shop + "/" + key +"/2/"
    upload_url3 = '/admin/blobimage/'+ shop + "/" + key +"/3/"
    dict = {'ITEM':item,'STORIES':stories,'BLOBURL':upload_url
        ,'BLOBURL1':upload_url1
        ,'BLOBURL2':upload_url2
        ,'BLOBURL3':upload_url3}
    dict['STORIES'] = stories
    context = Context(dict)
    response = render_to_response("admin/itemfull.html",context,context_instance=RequestContext(request))
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response
  else:
    return error.retailError(request,"item not found")

@userapi.authority_item
def saveitem(request,shop,key):
  __register_admin_action(request,"saveitem",shop+"/"+key)
  item = Item.get_by_id(int(key),parent = Supplier.getSupplierByName(shop))
  if(item):
    item.name = request.POST['name']
    item.refid = request.POST['refid']
    item.price = float(request.POST['price'])
    item.cost = float(request.POST['cost'])
    item.description = request.POST['description']
    item.specification = request.POST['spec']
    item.category = request.POST['category']
    item.category2 = request.POST['sndcategory']
    item.ebaycategory = request.POST['ebaycategory']
    item.disable = (True,False)[request.POST['disabled'] == "False"]
    item.put()
    indexItem(item)
  response =  HttpResponseRedirect('/admin/item/'+ shop + '/' + key +"/")
  return response


#### End Section

# Helper functions for fixing items 
# 


def clean(request):
  items = Item.all()
  for item in items:
    item.name = item.name.replace("\n","").replace("\t","").replace("\r","")
    item.put()
  items = SupplierItem.all()
  for item in items:
    item.description = item.description.replace("\n","").replace("\t","").replace("\r","")
    item.put()
  return HttpResponse("over")

# Config the website 
#
#
@userapi.authority_config
def feedinfo(k,content,type):
  if(type == "private"):
    configsite(k,content)
  else:
    line = ShopInfo.all().filter("name =",k).get()
    if not line:
      line = ShopInfo(name=k,content=content,type=type)
      line.put()
    else:
      line.content = content
      line.put()

@userapi.authority_config
def configsite(attr,content):
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
def preference(request):
  context = {}
  context['CATEGORIES'] = ShopInfo.all().filter("type =","category").order("name")
  context['SITEINFO'] = retailtype.getSiteInfo()
  return (render_to_response("config/preferences.html",context,context_instance=RequestContext(request)))

@userapi.authority_config
def ebayconfig(request):
#  some config template
  context = {}
  context['EBAY'] = ShopInfo.all().filter("type =","ebay").order("name")
  return (render_to_response("config/config.html",context,context_instance=RequestContext(request)))

@userapi.authority_config
def addconfig(request):
  if ("title" in request.POST):
    if ("content" in request.POST and request.POST['content']):
      feedinfo(request.POST['title'],request.POST['content'],request.POST['type'])
    else:
      line = ShopInfo.all().filter("name =",request.POST['title']).get()
      if line:
        line.delete()
  response =  HttpResponseRedirect('/admin/config/'+ request.POST['setting'])
  return response

@userapi.authority_config
def removeconfig(request):
  if ("title" in request.POST):
    line = ShopInfo.all().filter("name =",request.POST['title']).get()
    if line:
      line.delete()
  return HttpResponse("ok")

###################################### Scan and Fix Stuff ################################

####
# Main body of scan and fix items 
#
####

def fixitems(cursor=None, num_updated=0):
    query = Item.all()
    if cursor:
        query.with_cursor(cursor)
    to_put = []
    for item  in query.fetch(limit=100):
      if (item.disable == None):
        item.disable = False
      if (item.ebayid == None):
        item.ebayid = ""
      if (item.ebayid == ""):
        item.disable = True
      img = item.getImage(0)
      if img:
        img = ImageData(image=item.picture,name=item.name,parent=item,idx=0) 
      item.picture = None
      to_put.append(item)
    if to_put:
        db.put(to_put)
        num_updated += len(to_put)
        logging.debug(
            'Scan %d entities to Datastore for a total of %d',
            len(to_put), num_updated)
        deferred.defer(
            fixitems, cursor=query.cursor(), num_updated=num_updated)
    else:
        logging.debug(
            'Scan items complete with %d updates!', num_updated)
        return None
####
# Maintaince request
#
####

def scanitems(request):
  deferred.defer(fixitems)
  return HttpResponse('Item scanning successfully initiated.')
