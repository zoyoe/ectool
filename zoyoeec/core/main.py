import django.core.handlers.wsgi
from django.core.context_processors import csrf
from django.template import loader,Context,RequestContext
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from ebaysdk import finding
from ebaysdk.exception import ConnectionError
from ebayapi.ebay import ebay_view_prefix,getactivelist, getEbayInfo
from retail import retail, Supplier,Item,SiteInfo
import retailtype
from google.appengine.ext import db
from google.appengine.api import users,namespace_manager
from page import *
import record, random, json, error
import userapi

application = django.core.handlers.wsgi.WSGIHandler()

def main(request):
  if (request.META['HTTP_HOST']=="www.zoyoe.com"):
    # This is the main website
    stories = retailtype.getCategoriesInfo()
    fliers = retailtype.ShopInfo.all().filter("type =","category").order("name")
    context = Context({'STORIES':stories,'FLIERS':fliers})
    return (render_to_response("zoyoe/index.html",context,context_instance=RequestContext(request)))
  else:
    # This is customer's website
    site = retailtype.getSiteInfo()
    if site:
      if site.published:
        return retail(request)
      else:
        return HttpResponseRedirect('/admin/')
    else:
      return HttpResponseRedirect('/admin/config/preference/')
##
# Display the current status of the workspace ( main site )
# 
##
def workspace(request):
  ##  if (request.META['HTTP_HOST']=="www.zoyoe.com"):
  return (render_to_response("zoyoe/createworkspace.html",{},context_instance=RequestContext(request)))
  ## else:
  ##  return HttpResponseRedirect('/admin/config/preference/')

def logout(request):
  zuser = userapi.logoutUser(request)
  return HttpResponseRedirect('/')

def login(request):
  if (request.method == "POST"):
    if('email' in request.POST and 'password' in request.POST):
      email = request.POST['email']
      password = request.POST['password']
      zuser = userapi.loginUser(request,email,password)
      if zuser:
        if ('requesturl' in request.POST):
          requesturl = request.POST['requesturl']
          return HttpResponseRedirect(userapi.decrypt('url',requesturl));
        return error.ZoyoeSuccess("Success")
      else:
        if ('requesturl' in request.POST):
          requesturl = request.POST['requesturl']
          error.builderror(request,"User not exist or password not correct")
          return HttpResponseRedirect("/login/?requesturl=" + requesturl);
        else:
          return error.ZoyoeError("User not exist or password not correct")
    return error.ZoyoeError("email or password not provided")
  else:
    context = {};
    if ('requesturl' in request.GET):
      context['requesturl'] = request.GET['requesturl']
    return (render_to_response("zoyoe/login.html",context,context_instance=RequestContext(request)))

def register(request):
  if (request.method == "POST"):
    if('email' in request.POST and 'password' in request.POST):
      email = request.POST['email']
      password = request.POST['password']
      zuser = userapi.registerUser(request,email,password)
      if zuser:
        if ('requesturl' in request.GET):
          requesturl = request.GET['requesturl']
          return HttpResponseRedirect(userapi.decrypt('url',requesturl));
        else:
          return HttpResponseRedirect("/");
  # Pass to the phase as method neq POST 
  zuser = userapi.getCurrentUser(request)
  if not zuser:
    if ('requesturl' in request.GET):
      context = {}
      context['requesturl'] = request.GET['requesturl']
    return (render_to_response("zoyoe/register.html",context,context_instance=RequestContext(request)))
  else:
    if ('requesturl' in request.GET):
      requesturl = request.GET['requesturl']
      return HttpResponseRedirect(userapi.decrypt('url',requesturl));
    else:
      return HttpResponseRedirect("/");

def createworkspace(request):
  if retailtype.currentSite():
    return HttpResponseRedirect('/admin/config/preference/')
  else:
    if (request.method == "POST"):
      if('email' in request.POST and 'password' in request.POST):
        email = request.POST['email']
        password = request.POST['password']
        zuser = userapi.registerUser(request,email,password)
    zuser = userapi.getCurrentUser(request)
    if zuser:
      zuser.addAuthority(["ebay","config","item"])
      site = retailtype.getSiteInfo()
      site.put() # create the site
      return HttpResponseRedirect('/admin/config/preference/');
    else:
      return HttpResponseRedirect('/workspace/');

def items(request,shop,category):
  stories = retailtype.getCategoriesInfo()
  lvl1 = "Category"
  lvl2 = "Gallery"
  if (shop in stories):
    for c in stories[shop]:
      if (category in stories[shop][c]['children']):
        lvl1 = stories[shop][c]['name']
        lvl2 = stories[shop][c]['children'][category]['name']
  else:
    return error.ZoyoeError("category does not exist")
  dict = {'SHOP':shop,'ITEM_WIDTH':'200','STORIES':stories,'PATH':lvl1,'CATEGORY':lvl2}
  query = retailtype.getCategoryItems(category).filter("disable ==",False)
  myPagedQuery = PagedQuery(query, 12)
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
  temp_path = retailtype.getSiteInfo().getTemplate("products.html");
  return (render_to_response(temp_path,context,context_instance=RequestContext(request)))

def item(request,shop,key):
  stories = retailtype.getCategoriesInfo()
  item = Item.get_by_id(int(key),parent = Supplier.getSupplierFromName(shop))
  return record.getItemResponse(request,item,stories)

### This is the main view of pos #
@userapi.authority_config
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

@userapi.authority_item
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
  context = Context({'sellitems':items
   ,'STORIES':stories,'STAT':stat,'ESTAT':estat})
  return (render_to_response("admin/dashboard.html",context,context_instance=RequestContext(request)))


def buildPreviewContext(request,max,config=False):
  contextdic = {}
  finddic = {}
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

### FIXME: It is bad to have the entry point of ebay plugin at the moment
### 
###
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


@userapi.authority_item
def pdforder(request):
  context = {}
  return (render_to_response("order/pdforder.html",context,context_instance=RequestContext(request)))

@userapi.authority_item
def csvorder(request):
  context = {}
  return (render_to_response("order/csvorder.html",context,context_instance=RequestContext(request)))

def namespace(request):
  return HttpResponse(namespace_manager.get_namespace())


