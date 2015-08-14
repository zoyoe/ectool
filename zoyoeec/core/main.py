import django.core.handlers.wsgi
from django.core.context_processors import csrf
from django.template import loader,Context,RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
from ebaysdk import finding
from ebaysdk.exception import ConnectionError
from ebay import ebay_view_prefix,getactivelist, getEbayInfo
from retail import getSupplier,saveSupplier,getSupplierFromEbayInfo,Supplier,Item,SiteInfo
import random,json
from retailtype import getCategoryItems,siteinfo,ShopInfo
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import namespace_manager
from page import *
import zuser
import record

application = django.core.handlers.wsgi.WSGIHandler()

def retail(request):
  stories = siteinfo()
  fliers = ShopInfo.all().filter("type =","category").order("name")
  context = Context({'RETAIL': True,'ITEM_WIDTH':'200','STORIES':stories,'FLIERS':fliers})
  return (render_to_response("retailcover.html",context,context_instance=RequestContext(request)))

def products(request):
  stories = siteinfo()
  items = Item.all().filter("ebayid !=",None).filter("ebayid !=","").fetch(100)
  context = Context({'RETAIL': True,'ITEM_WIDTH':'200','STORIES':stories,'sellitems':items})
  return (render_to_response("products/gallery.html",context,context_instance=RequestContext(request)))


def allebayitems(request):
  stories = siteinfo()
  items = Item.all().filter("ebayid !=",None).filter("ebayid !=","")
  context = Context({'RETAIL': True,'ITEM_WIDTH':'200','STORIES':stories,'sellitems':items})
  return (render_to_response("admin/allebayitems.html",context,context_instance=RequestContext(request)))

def items(request,shop,category):
  stories = siteinfo()
  lvl1 = "Category"
  lvl2 = "Gallery"
  for c in stories[shop]:
    if (category in stories[shop][c]['children']):
      lvl1 = stories[shop][c]['name']
      lvl2 = stories[shop][c]['children'][category]['name']
  dict = {'SHOP':shop,'ITEM_WIDTH':'200','STORIES':stories,'PATH':lvl1,'CATEGORY':lvl2}
  query = getCategoryItems(category)
  myPagedQuery = PagedQuery(query, 24)
  items = []
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
  if (idx != 0):
    dict['queryurlprev'] = "/items/"+shop+"/"+category +"/?page="+str(idx-1)
  if (idx < dict['pages']):
    dict['queryurlnext'] = "/items/"+shop+"/"+category +"/?page="+str(idx+1)
  dict['sellitems'] = items
  dict['queryurl'] = "/items/"+shop+"/"+category
  context = Context(dict)
  return (render_to_response("retail.html",context,context_instance=RequestContext(request)))

def item(request,shop,key):
  stories = siteinfo()
  item = Item.get_by_id(int(key),parent = getSupplier(shop))
  return record.getItemResponse(request,item,stories)

### This is the main view of pos #
@zuser.authority_config
@ebay_view_prefix
def pos(request):
  cart = request.session.get('cart',{})
  ebayinfo = getEbayInfo(request)
  if not cart:
    cart = {}
  context = Context({'CART':cart.values(),'ebayinfo':ebayinfo})
  return (render_to_response("pos.html",context,context_instance=RequestContext(request)))

class dashboard:
  totalsuppliers = 0
  totalcategories = 0

@zuser.authority_item
@ebay_view_prefix
def admin(request):
  suppliers = Supplier.all()
  stories = {}
  stat = {}
  estat = {}
  items = []
  for supply in suppliers:
    stories[supply.name] = json.loads(supply.data)
    stat[supply.name] = supply.getStat()
    estat[supply.name] = supply.getEbayStat()
  ebayinfo = getEbayInfo(request)
  if ebayinfo:
    supplier = getSupplierFromEbayInfo(ebayinfo)
    if (supplier):
      context = Context({'ebayinfo':ebayinfo,'sellitems':items
       ,'STORIES':stories,'STAT':stat,'ESTAT':estat})
      return (render_to_response("intro.html",context,context_instance=RequestContext(request)))
    else:
      context = Context({'ebayinfo':ebayinfo,'sellitems':[]
       ,'STORIES':stories})
      return (render_to_response("intro.html",context,context_instance=RequestContext(request)))

def find(request):
  api = finding(siteid='EBAY-AU',appid = 'zoyoea269-b772-4c8d-98bb-e8a23cefc0e');
  api.execute('findItemsAdvanced',
    {'itemFilter':[{'name':'Seller','value':'p_ssg'}]
    })
  return HttpResponse(str(api.response_dict()))

def buildPreviewContext(request,max,config=False):
  contextdic = {}
  contextdic['APP_HOST'] = request.META['HTTP_HOST'] 
  contextdic.update(csrf(request))
  if ('keywords' in request.GET):
    finddic['keywords'] = request.GET['keywords']
    contextdic['KEYWORDS'] = request.GET['keywords']
  if not config:
    try:
      sellerid = request.GET['sellerid']
      finddic = {'itemFilter':[{'name':'Seller','value':sellerid}]}
      contextdic['SELLER_ID'] = sellerid
      api = finding(siteid='EBAY-AU',appid = 'zoyoea269-b772-4c8d-98bb-e8a23cefc0e');
      api.execute('findItemsAdvanced', finddic)
      dict = api.response_dict()
      result_count = int(str(dict.searchResult['count'].value))
      contextdic['ITEM_WIDTH'] = '200'
      if (result_count > 0):
        items = dict.searchResult['item']
        random.shuffle(items)
        contextdic['sellitems'] = items[0:12]
      else:
        contextdic['sellitems'] = []
    except ConnectionError as estr:
      contextdic['sellitems'] = []
    return contextdic
  else:
    return contextdic

### A view that returns all the recepits 
###
@ebay_view_prefix
def receipts(request):
  receipts = db.GqlQuery("SELECT * FROM Receipt")
  context = Context({'receipts':receipts,'ebayinfo':getEbayInfo(request)})
  return (render_to_response("receipts/receipts.html",context,context_instance=RequestContext(request)))

@ebay_view_prefix
def config(request):
  context = buildPreviewContext(request,20,True)
  context['ebayinfo'] = getEbayInfo(request)
  return (render_to_response("config.html",context,context_instance=RequestContext(request)))

def ebay(request):
  context = buildPreviewContext(request,20)
  response = render_to_response("ebay.html",context,mimetype="text")
  response['Access-Control-Allow-Origin']  = "*"
  return response

def ebayjson(request):
  context = buildPreviewContext(request,20)
  rslt = "" 
  for item in context['sellitems']:
    rslt += item['viewItemURL']['value']
    rslt += "," + item['galleryURL']['value']
    rslt += "," + item['title']['value']
    rslt += "," + item['sellingStatus']['currentPrice']['value']
    rslt += ","
  response = HttpResponse(rslt,mimetype="text")
  response['Access-Control-Allow-Origin']  = "*"
  return response


@zuser.authority_item
def order(request):
  context = {}
  return (render_to_response("order.html",context,context_instance=RequestContext(request)))

def namespace(request):
  return HttpResponse(namespace_manager.get_namespace())


