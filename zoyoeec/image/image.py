import django.core.handlers.wsgi
from core import zuser
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
from order import *
from error import *
from page import *
from core.retailtype import Supplier,Item,ShopInfo,ImageData,formatName### Reource view

def __createsc(img_data):
  image = images.Image(img_data)
  image.resize(width=300)
  return image.execute_transforms()

def __quickrescale(img_data, size):
  image = images.Image(img_data)
  if image.width > image.height:
    image.resize(width=size)
    return image.execute_transforms()
  else:
    image.resize(height=size)
    return image.execute_transforms()


def __rescale(img_data, width, height, halign='middle', valign='middle'):
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



##
# fetch the first image of a item by its refid
# FIXME: dont create small images all the time
##
@zuser.authority_item
def fetchimagebyrid(request,itemid):
  picture = None
  item = Item.getItemByRID(itemid)
  if item:
    image = item.getImage(0)
    if image:
      if ("sc" in request.GET):
         if image.small:
            picture = image.small
         elif image.image:
            image.small = __createsc(image.image)
            try:
              image.put()
            except RequestTooLargeError:
              pic = __rescale(image.image,600,600)
              image.image = pic
              image.put()
              del pic
            picture = image.small
         else:
            picture = None
      else:
         picture = image.image
    else:
      picture = None
  else:
    picture = None
  if picture:
    return HttpResponse(picture, mimetype="image/jpeg")
  else:
    return  HttpResponseRedirect('/static/res/picnotfound.jpg')


def fetchimage(request,supplier,key,index="0"):
  item = Item.get_by_id(int(key),parent = Supplier.getSupplierByName(supplier))
  picture = None
  idx = int(index)
  if item:
    image = item.getImage(idx)
    if image:
      if ("sc" in request.GET):
         if image.small:
            picture = image.small
         elif image.image:
            image.small = __createsc(image.image)
            try:
              image.put()
            except RequestTooLargeError:
              pic = __rescale(image.image,600,600)
              image.image = pic
              image.put()
              del pic
            picture = image.small
         else:
            picture = None
      else:
         picture = image.image
    else:
      picture = None
  else:
    picture = None
  if picture:
    return HttpResponse(picture, mimetype="image/jpeg")
  else:
    return  HttpResponseRedirect('/static/res/picnotfound.jpg')

# Used for uploading image files


##
# FIXME: This should be moved into rest api
#
##
def rotateimage(request,supplier,key,index="0"):
  item = Item.get_by_id(int(key),parent = Supplier.getSupplierByName(supplier))
  idx = int(index)
  if item:
    image = item.getImage(int(idx))
    if image:
      gimg = images.Image(image.image)
      gimg.rotate(90)
      image.image = gimg.execute_transforms()
      image.put()
  return HttpResponse("ok")

###
# 
# Uploading image for item
#
###
@zuser.authority_item
def uploadimage(request,supplier,key,index='0'):
  # FIXME: need to think about how to record this activity
  #__register_admin_action(request,"uploadimage",supplier + "/" + key + "/" + index)
  
  #type = request.FILES['image'].content_type
  #image = request.FILES['image'].content_type_extra
  image_data = request.FILES['image'].read()
  picture = __rescale(image_data,600,600)
  item = Item.get_by_id(int(key),parent = Supplier.getSupplierByName(supplier))
  idx = int(index)
  if item:
    img = item.getImage(idx)
    if img:
      img.image = picture
    else:
      img = ImageData(image=picture,name=item.name,parent=item,idx=idx) 
      img.url = "http://" + request.META['HTTP_HOST'] + "/admin/fetchimage/" + supplier + "/" + key + "/" + str(idx)
    img.small = __createsc(picture)
    img.put()
    del picture
    item.galleryurl = img.url
    item.put()
    return HttpResponse("ok")
  else:
    return HttpResponse("fail")

# ####
# return ZoyoeSuccess if images are added
# ####
@csrf_exempt
@zuser.authority_item
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
    img.small = createsc(img.image)
    img.put()
  else:
    img = ImageData(image=picture,name=item.name,parent=item,idx=idx) 
    img.url = "http://" + request.META['HTTP_HOST'] + "/admin/fetchimage/" + item.parent().name + "/" + str(item.key().id()) + "/" + str(idx)
    img.small = createsc(img.image)
    img.put()
    del picture
    item.galleryurl = img.url
    item.put()
  return HttpResponse("ok")


####
#  A view for userd to upload multiply images for a supplier
#
####
@zuser.authority_item
def uploadimages(request):
  supplier = "Anonymous"
  if 'supplier' in request.GET:
    supplier = request.GET['supplier']
  context = {'SUPPLIER':supplier}
  return (render_to_response("admin/images.html",context,context_instance=RequestContext(request)))


####
# Fix urls for ImageData
# FIXME: using task queue instead
#
####
def checkurl(request):
  imgs = ImageData.all()
  for img in imgs:
    img.url = "http://" + request.META['HTTP_HOST'] + "/admin/fetchimage/" + img.parent().parent().name + "/" + str(img.parent().key().id()) + "/" + str(img.idx) +"/"
    img.put()
  return HttpResponse("ok")

