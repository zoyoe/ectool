import django.core.handlers.wsgi
from django import forms
from django.core.context_processors import csrf
from django.template import loader,Context,RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from retail import getSupplier,saveSupplier,getSupplierFromEbayInfo,Supplier,Item,ShopInfo,ImageData,formatName
import ebayapi
import zuser
from google.appengine.ext import db,blobstore
from google.appengine.api import users
from django.views.decorators.cache import never_cache
from google.appengine.api import images
import datetime
import urllib2,httplib,random,json
from urllib import urlencode
from ebay import ebay_view_prefix,ebay_ajax_prefix,getinactivelist,getactivelist, getEbayInfo, sync, format
from order import *
from error import *
from page import *
from django.views.decorators.csrf import csrf_exempt, csrf_protect

application = django.core.handlers.wsgi.WSGIHandler()

class AdminAction(db.Model):
  date = db.DateProperty(auto_now_add = True)
  action = db.StringProperty(required = True)
  target = db.StringProperty(required = True)

def registerAdminAction(action,target):
  user = zuser.getCurrentUser()
  action = AdminAction(action = action,target=target,parent=user)
  action.put()

def actionhistory(request):
  dict = {}
  dict['actions'] = pageItems(AdminAction.all().order("-date"),
      dict,"/admin/actionhistory/",request)
  context = Context(dict)
  return (render_to_response("./admin/history.html",context,context_instance=RequestContext(request)))

@zuser.authority_item
def unpublisheditems(request,shop):
  supplier = getSupplier(shop)
  dict = {'SHOP':shop,'ITEM_WIDTH':'200'}
  if (supplier):
    dict['sellitems'] = pageItems(supplier.getUnpublishedItems(),dict,
        "/admin/items/"+shop+"/",request)
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))
  else:
    dict['sellitems'] = []
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))



@zuser.authority_item
def ebayitems(request,shop):
  supplier = getSupplier(shop)
  dict = {'SHOP':shop,'ITEM_WIDTH':'200'}
  if (supplier):
    #dict['sellitems'] = pageItems(supplier.getEbayItems(),
    #    dict,"/admin/items/"+shop+"/",request)

    dict['sellitems'] = supplier.getEbayItems()
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))
  else:
    dict['sellitems'] = []
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))

# standard paged query, fill context needed for paging
#
def pageItems(query,dict,url,request):
  myPagedQuery = PagedQuery(query,48)
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


@zuser.authority_item
def items(request,shop,category):
  supplier = getSupplier(shop)
  suppliers = Supplier.all()
  stories = {}
  lvl1 = "Category"
  lvl2 = "Gallery"
  for supply in suppliers:
    stories[supply.name] = json.loads(supply.data)
    if (supply.name == shop):
      for c in stories[supply.name]:
        if (category in stories[supply.name][c]['children']):
          lvl1 = stories[supply.name][c]['name']
          lvl2 = stories[supply.name][c]['children'][category]['name']
  dict = {'SHOP':shop,'ITEM_WIDTH':'200','STORIES':stories,'PATH':lvl1,'CATEGORY':lvl2}
  if (supplier):
    dict['sellitems'] = pageItems(supplier.getCategoryItems(category),
        dict,"/admin/items/"+shop+"/" + category + "/",request)
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))
  else:
    dict['sellitems'] = []
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))

def supplieritems(request,shop): 
  supplier = getSupplier(shop)
  suppliers = [supplier]
  stories = {}
  lvl1 = "Category"
  lvl2 = "Gallery"
  for supply in suppliers:
    stories[supply.name] = json.loads(supply.data)
  dict = {'SHOP':shop,'ITEM_WIDTH':'200','STORIES':stories,'PATH':'All','CATEGORY':''}
  if (supplier):
    dict['sellitems'] = pageItems(supplier.getItems(),
        dict,"/admin/items/" + shop + "/",request)
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))
  else:
    dict['sellitems'] = []
    context = Context(dict)
    return (render_to_response("./admin/items.html",context,context_instance=RequestContext(request)))

@zuser.authority_item
def additem(request):
  rid = request.GET['rid']
  item = createDefaultItem(rid)
  response =  HttpResponseRedirect('/admin/item/'+ item.parent().name + '/' + str(item.key().id()) +"/")
  return response
  
@zuser.authority_item
def item(request,shop,key):
  stories = siteinfo()
  item = Item.get_by_id(int(key),parent = getSupplier(shop))
  if item:
    upload_url = blobstore.create_upload_url('/admin/blobimage/'+key +"/0/")
    upload_url1 = blobstore.create_upload_url('/admin/blobimage/'+key +"/1/")
    upload_url2 = blobstore.create_upload_url('/admin/blobimage/'+key +"/2/")
    upload_url3 = blobstore.create_upload_url('/admin/blobimage/'+key +"/3/")
    dict = {'ITEM':item,'STORIES':stories,'BLOBURL':upload_url
        ,'BLOBURL1':upload_url1
        ,'BLOBURL2':upload_url2
        ,'BLOBURL3':upload_url3}
    dict['STORIES'] = stories
    context = Context(dict)
    response = render_to_response("admin/item.html",context,context_instance=RequestContext(request))
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response
  else:
    return retailError(request,"item not found")

@zuser.authority_item
def deleteitem(request,shop,key):
  item = Item.get_by_id(int(key),parent = getSupplier(shop))
  if item:
    deleteItemIndex(item)
    item.delete()
  return HttpResponseRedirect('/admin/items/'+shop)

@zuser.authority_item
def itemimage(request,shop,key):
  suppliers = Supplier.all()
  stories = {}
  items = []
  for supply in suppliers:
    stories[supply.name] = json.loads(supply.data)
  item = Item.get_by_id(int(key),parent = getSupplier(shop))
  if(item):
    upload_url = blobstore.create_upload_url('/admin/blobimage/'+ shop + "/" + key +"/0/")
    upload_url1 = blobstore.create_upload_url('/admin/blobimage/'+ shop + "/" + key +"/1/")
    upload_url2 = blobstore.create_upload_url('/admin/blobimage/'+ shop + "/" + key +"/2/")
    upload_url3 = blobstore.create_upload_url('/admin/blobimage/'+ shop + "/" + key +"/3/")
    upload_url = '/admin/blobimage/'+ shop + "/" + key +"/0/"
    upload_url1 = '/admin/blobimage/'+ shop + "/" + key +"/1/"
    upload_url2 = '/admin/blobimage/'+ shop + "/" + key +"/2/"
    upload_url3 = '/admin/blobimage/'+ shop + "/" + key +"/3/"
    dict = {'ITEM':item,'STORIES':stories,'BLOBURL':upload_url
        ,'BLOBURL1':upload_url1
        ,'BLOBURL2':upload_url2
        ,'BLOBURL3':upload_url3}
    context = Context(dict)
    return (render_to_response("admin/image.html",context,context_instance=RequestContext(request)))

@zuser.authority_item
def saveitem(request,shop,key):
  registerAdminAction("saveitem",shop+"/"+key)
  item = Item.get_by_id(int(key),parent = getSupplier(shop))
  if(item):
    item.name = request.POST['name']
    item.price = float(request.POST['price'])
    item.cost = float(request.POST['cost'])
    item.description = request.POST['description']
    item.specification = request.POST['spec']
    item.category = request.POST['category']
    item.category2 = request.POST['sndcategory']
    item.ebaycategory = request.POST['ebaycategory']
    item.put()
    indexItem(item)
  response =  HttpResponseRedirect('/admin/item/'+ shop + '/' + key +"/")
  return response

def fetchimage(request,shop,key,index="0"):
  item = Item.get_by_id(int(key),parent = getSupplier(shop))
  picture = None
  idx = int(index)
  if item:
    image = item.getImage(idx)
    if image:
      picture = image.image
    else:
      picture = None
  else:
    picture = None
  if picture:
    return HttpResponse(picture, mimetype="image/jpeg")
  else:
    return  HttpResponseRedirect('/static/res/picnotfound.jpg')

def rotateimage(request,shop,key,index="0"):
  item = Item.get_by_id(int(key),parent = getSupplier(shop))
  idx = int(index)
  if item:
    image = item.getImage(int(idx))
    if image:
      gimg = images.Image(image.image)
      gimg.rotate(90)
      image.image = gimg.execute_transforms()
      image.put()
  return HttpResponse("ok")

def quickrescale(img_data, size):
  image = images.Image(img_data)
  if image.width < image.height:
    image.resize(width=size)
    return image.execute_transforms()
  else:
    image.resize(height=size)
    return image.execute_transforms()




def rescale(img_data, width, height, halign='middle', valign='middle'):
  """Resize then optionally crop a given image.

  Attributes:
    img_data: The image data
    width: The desired width
    height: The desired height
    halign: Acts like photoshop's 'Canvas Size' function, horizontally
            aligning the crop to left, middle or right
    valign: Verticallly aligns the crop to top, middle or bottom

  """
  image = images.Image(img_data)

  desired_wh_ratio = float(width) / float(height)
  wh_ratio = float(image.width) / float(image.height)

  if desired_wh_ratio > wh_ratio:
    # resize to width, then crop to height
    image.resize(width=width)
    image.execute_transforms()
    trim_y = (float(image.height - height) / 2) / image.height
    if valign == 'top':
      image.crop(0.0, 0.0, 1.0, 1 - (2 * trim_y))
    elif valign == 'bottom':
      image.crop(0.0, (2 * trim_y), 1.0, 1.0)
    else:
      image.crop(0.0, trim_y, 1.0, 1 - trim_y)
  else:
    # resize to height, then crop to width
    image.resize(height=height)
    image.execute_transforms()
    trim_x = (float(image.width - width) / 2) / image.width
    if halign == 'left':
      image.crop(0.0, 0.0, 1 - (2 * trim_x), 1.0)
    elif halign == 'right':
      image.crop((2 * trim_x), 0.0, 1.0, 1.0)
    else:
      image.crop(trim_x, 0.0, 1 - trim_x, 1.0)

  return image.execute_transforms()

@zuser.authority_item
def blobimage(request,shop,key,index='0'):
  registerAdminAction("blobimage",shop+"/"+key)
  #file = request.FILES['image'].read()
  #type = request.FILES['image'].content_type
  #image = request.FILES['image'].content_type_extra
  file = request.FILES['image'].read()
  picture = rescale(file,800,800)
  item = Item.get_by_id(int(key),parent = getSupplier(shop))
  idx = int(index)
  if item:
    img = item.getImage(idx)
    if img:
      img.image = picture
      img.put()
    else:
      img = ImageData(image=picture,name=item.name,parent=item,idx=idx) 
      img.url = "http://" + request.META['HTTP_HOST'] + "/admin/fetchimage/" + shop + "/" + key + "/" + str(idx)
      img.put()
    del picture
    item.galleryurl = img.url
    item.put()
    return HttpResponse("ok")
  else:
    return HttpResponse("fail")

@zuser.authority_ebay
@ebay_view_prefix
def exporttoebay(request,shop,key):
  registerAdminAction("ebayexport",shop+"/"+key)
  token = ebay.getToken(request)
  item = Item.get_by_id(int(key),parent = getSupplier(shop))
  if item:
    if (item.ebayid and (item.ebayid != '0')):
      info = ebay.getEbayInfo(request)
      rslt = sync(info,item)
      return HttpResponse(rslt,mimetype="text/xml")
    rslt = ebayapi.api.AddItem(token,item)
    xml_doc = etree.parse(StringIO(rslt))
    ack = xml_doc.xpath("//xs:Ack",
      namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
    if(not 'Failure' in ack.text):
      itemid = xml_doc.xpath("//xs:ItemID",
        namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
      item.ebayid = itemid
      item.put()
    return HttpResponse(rslt,mimetype="text/xml")

@ebay_ajax_prefix
def importfromebay(ebayinfo,itemid):
  (rslt,item) = format(ebayinfo,itemid)
  registerAdminAction("ebaydepoly",item.parent().name+"/"+str(item.key().id()))
  return rslt
  

@ebay_view_prefix
def syncwithebay(request,shop,key):
  registerAdminAction("ebayexport",shop+"/"+key)
  info = ebay.getEbayInfo(request)
  item = Item.get_by_id(int(key),parent = getSupplier(shop))
  if item:
    rslt = sync(info,item)
    return HttpResponse(rslt,mimetype="text/xml")

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

def replaceimage(request):
  items = Item.all()
  for item in items:
    if(item.picture):
      img = ImageData(image=item.picture,name=item.name,parent=item,idx=0) 
      img.url = "http://" + request.META['HTTP_HOST'] + "/admin/fetchimage/" + img.parent().parent().name + "/" + str(img.parent().key().id()) + "/0/"
      img.put()
      item.picture = None
      item.put()
    image = item.getImage(0)
    if image:
      item.galleryurl = image.url
      item.put()
  return HttpResponse("ok")


def checkurl(request):
  imgs = ImageData.all()
  for img in imgs:
    img.url = "http://" + request.META['HTTP_HOST'] + "/admin/fetchimage/" + img.parent().parent().name + "/" + str(img.parent().key().id()) + "/" + str(img.idx) +"/"
    img.put()
  return HttpResponse("ok")

# Config the website 
#
#
#
@zuser.authority_config
def feedinfo(k,content,type):
  line = ShopInfo.all().filter("name =",k).get()
  if not line:
    line = ShopInfo(name=k,content=content,type=type)
    line.put()
  else:
    line.content = content
    line.put()

@zuser.authority_config
@ebay_view_prefix
def categories(request):
  context = {}
  context['CATEGORIES'] = ShopInfo.all().filter("type =","category").order("name")
  return (render_to_response("config/categories.html",context,context_instance=RequestContext(request)))

@zuser.authority_config
def ebayconfig(request):
#  some config template
  context = {}
  context['EBAY'] = ShopInfo.all().filter("type =","ebay").order("name")
  return (render_to_response("config/config.html",context,context_instance=RequestContext(request)))

@zuser.authority_config
def addconfig(request):
  if ("title" in request.POST):
    feedinfo(request.POST['title'],request.POST['content'],request.POST['type'])
  return HttpResponse("ok")


@zuser.authority_config
def removeconfig(request):
  if ("title" in request.POST):
    line = ShopInfo.all().filter("name =",request.POST['title']).get()
    if line:
      line.delete()
  return HttpResponse("ok")



@zuser.authority_ebay
@ebay_view_prefix
def deploy(request):
  context = {}
  context['itemlist'] = getactivelist(request)
  #request.session['ebayinfo'] = {}
  context['ebayinfo'] = getEbayInfo(request)
  site = SiteInfo.all().get()
  if not site:
    site = SiteInfo()
  site.mainshop = formatName(context['ebayinfo']['store'])
  site.put()
  saveSupplier(context['ebayinfo'])
  return (render_to_response("insert.html",context,context_instance=RequestContext(request)))


@zuser.authority_ebay
@ebay_view_prefix
def relist(request):
  context = {}
  context['itemlist'] = getinactivelist(request)
  return (render_to_response("insert.html",context,context_instance=RequestContext(request)))



@zuser.authority_item
@ebay_view_prefix
def uploadimages(request):
  supplier = "Anonymous"
  if 'supplier' in request.GET:
    supplier = request.GET['supplier']
  context = {'SUPPLIER':supplier}
  return (render_to_response("admin/images.html",context,context_instance=RequestContext(request)))

@csrf_exempt
@zuser.authority_item
@ebay_view_prefix
def addimages(request,supplier):
  file = request.FILES['files[]'].read()
  name = request.FILES['files[]'].name.split(".")
  name.pop()
  rid = ".".join(name)
  item = createDefaultItem(rid,supplier)
  picture = quickrescale(file, 600)
  idx = 0
  img = item.getImage(idx)
  if img:
    img.image = picture
    img.put()
  else:
    img = ImageData(image=picture,name=item.name,parent=item,idx=idx) 
    img.url = "http://" + request.META['HTTP_HOST'] + "/admin/fetchimage/" + item.parent().name + "/" + str(item.key().id()) + "/" + str(idx)
    img.put()
    del picture
    item.galleryurl = img.url
    item.put()
  return HttpResponse("ok")


def setupinfo(request):
  lines = ShopInfo.all()
  for line in lines:
    line.type = "ebay"
    line.put()
  return HttpResponse("ok")

def cleanitems(request):
  items = Item.all()
  for item in items:
    if(item.parent()==None):
      deleteItemIndex(item)
      item.delete()
  return HttpResponse("ok")

      
     
