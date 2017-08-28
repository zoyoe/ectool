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
from core import error, dbtype, userapi, page
from model import *
import string, logging

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

####
#  This is the default view for admin
#
####
@userapi.authority_item
def admin(request):
  suppliers = dbtype.Supplier.all()
  stories = {}
  stat = {}
  estat = {}
  items = []
  for supply in suppliers:
    stories[supply.name] = json.loads(supply.data)
    stat[supply.name] = supply.getStat()
    estat[supply.name] = supply.getEbayStat()
  context = Context({'sellitems':items
   ,'STORIES':stories,'STAT':stat,'ESTAT':estat})
  return (render_to_response("admin/dashboard.html",context,context_instance=RequestContext(request)))



####
#  View of the action history 
#
####
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
def items(request,command,path):
  (suppliername,category) = string.split(path+"/","/",1)
  dict = {'PATH' : path, 'ITEM_WIDTH':'200'}
  category = category.split("/")[0]
  if suppliername:
    supplier = dbtype.Supplier.getSupplierByName(suppliername)
    if supplier:
      dict['ITEMS'] = pageItems(supplier.getItems(command,category),dict,
                      "/admin/items/" + command + "/" + path, request)
    else:
      dict['ITEMS'] = []
  else:
    dict['ITEMS'] = pageItems(dbtype.Item.all(),dict,
                      "/admin/items/" + command + "/" + path, request)
  context = Context(dict)
  return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))
  
def jsonSearch(dic, follow,  hd, target):
  for key in dic:
    if(key == target):
      return hd.insert(0,(key, dic[key]))
    else:
      if (jsonSearch(dic[key][follow]),hd,target):
        return hd.insert(0,(key, dic[key]))
      else:
        pass
  return None
    
#### End Section 


#### Section: Item manipulation views.

@userapi.authority_item
def additem(request):
  rid = request.GET['rid']
  item = dbtype.createDefaultItem(rid)
  response =  HttpResponseRedirect('/admin/item/'+ item.parent().name + '/' + str(item.key().id()) +"/")
  return response
  

@userapi.authority_item
def deleteitem(request,shop,key):
  item = dbtype.Item.get_by_id(int(key),parent = dbtype.Supplier.getSupplierByName(shop))
  if item:
    item.deleteIndex()
    item.delete()
  return HttpResponseRedirect('/admin/items/'+shop)

@userapi.authority_item
def item(request,shop,key):
  stories = dbtype.getCategoriesInfo()
  item = dbtype.Item.get_by_id(int(key),parent = dbtype.Supplier.getSupplierByName(shop))
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
  register_admin_action(request,"saveitem",shop+"/"+key)
  item = dbtype.Item.get_by_id(int(key),parent = dbtype.Supplier.getSupplierByName(shop))
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
    item.addItem(item)
  response =  HttpResponseRedirect('/admin/item/'+ shop + '/' + key +"/")
  return response


#### End Section

# Helper functions for fixing items 
# 


def clean(request):
  items = dbtype.Item.all()
  for item in items:
    item.name = item.name.replace("\n","").replace("\t","").replace("\r","")
    item.put()
  items = dbtype.SupplierItem.all()
  for item in items:
    item.description = item.description.replace("\n","").replace("\t","").replace("\r","")
    item.put()
  return HttpResponse("over")

   

@userapi.authority_config
def preference(request):
  context = {}
  suppliers = dbtype.Supplier.all()
  context['SUPPLIERS'] = suppliers
  context['SITE'] = dbtype.getSiteInfo()
  return (render_to_response("config/preferences.html",context,context_instance=RequestContext(request)))

@userapi.authority_config
def user(request):
  context = {}
  context['CATEGORIES'] = dbtype.getShopInfoByType("category")
  context['SITEINFO'] = dbtype.getSiteInfo()
  context['ACTIONS'] = pageItems(AdminAction.all().order("-date"),
      context,"/admin/actionhistory/",request)
  return (render_to_response("config/user.html",context,context_instance=RequestContext(request)))


@userapi.authority_config
def ebayconfig(request):
#  some config template
  context = {}
  context['EBAY'] = dbtype.getShopInfoByType("ebay")
  return (render_to_response("config/config.html",context,context_instance=RequestContext(request)))


###################################### Scan and Fix Stuff ################################

####
# Main body of scan and fix items 
#
####

def fixitems(cursor=None, num_updated=0):
    query = dbtype.Item.all()
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
        img = dbtype.ImageData(image=item.picture,name=item.name,parent=item,idx=0) 
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

"""
Requests for Maintaince:

"""

def scanitems(request):
  deferred.defer(fixitems)
  return HttpResponse('Item scanning successfully initiated.')
