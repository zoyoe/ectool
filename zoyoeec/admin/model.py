import django.core.handlers.wsgi
from core import zuser, retailtype
import ebay
import datetime,urllib2,httplib,random,json
from django import forms
from django.core.context_processors import csrf
from google.appengine.ext import db,blobstore,deferred
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.runtime.apiproxy_errors import RequestTooLargeError 
from ebay.ebay import ebay_view_prefix,ebay_ajax_prefix,getinactivelist,getactivelist, getEbayInfo, sync,relist, format
from order import *
from error import *
from page import *
from core.retailtype import Supplier,Item,ShopInfo,ImageData,formatName
from admin import jsonapi

class AdminAction(db.Model):
  date = db.DateProperty(auto_now_add = True)
  action = db.StringProperty(required = True)
  target = db.StringProperty(required = True)

def __register_admin_action(request,action,target):
  user = zuser.getCurrentUser(request)
  action = AdminAction(action = action,target=target,parent=user)
  action.put()

