import django.core.handlers.wsgi
import ebayapi,zuser,retailtype
import datetime,urllib2,httplib,random,json
from django import forms
from django.core.context_processors import csrf
from google.appengine.ext import db,blobstore,deferred
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.runtime.apiproxy_errors import RequestTooLargeError 
from ebay import ebay_view_prefix,ebay_ajax_prefix,getinactivelist,getactivelist, getEbayInfo, sync,relist, format
from order import *
from error import *
from page import *
from retail import Supplier,Item,ShopInfo,ImageData,formatName
from admin import json

class AdminAction(db.Model):
  date = db.DateProperty(auto_now_add = True)
  action = db.StringProperty(required = True)
  target = db.StringProperty(required = True)

def __register_admin_action(request,action,target):
  user = zuser.getCurrentUser(request)
  action = AdminAction(action = action,target=target,parent=user)
  action.put()

def createsc(img_data):
  image = images.Image(img_data)
  image.resize(width=300)
  return image.execute_transforms()

def quickrescale(img_data, size):
  image = images.Image(img_data)
  if image.width > image.height:
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

