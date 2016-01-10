import django.core.handlers.wsgi
from django.template import loader,Context,RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from ebaysdk import finding
from ebaysdk.exception import ConnectionError
from error import *
from lxml import etree
from StringIO import StringIO
import random,json
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import namespace_manager

class UserInfo(db.Model):
  email = db.StringProperty(default='xgao@zoyoe.com')
  ebaytoken = db.TextProperty(default=None)
  authtoken = db.StringProperty(default="[]")
  history = db.TextProperty(default="{}")

def getUser(email,createifnotexist):
  user = UserInfo.all().filter("email =",email).get()
  if (not user and createifnotexist):
    user = UserInfo(email = email)
    user.put()
  return user

def getCurrentUser():
  user = users.get_current_user()
  if user:
    return getUser(user.email(),True)
  else:
    return None

def checkAuthority(authority,user):
  if not user:
    return false
  totauth = json.loads(user.authtoken)
  if (any(authority in s for s in totauth)):
    return True
  else:
    return False

def authority_login(handler):
  def rst_handler(request,*args,**kargs):
    user = getCurrentUser()
    if user:
      return handler(request,*args,**kargs)
    else:
      return loginError(request,"Please login with your google account continue");
  return rsthandler

def authority_item(handler):
  def rst_handler(request,*args,**kargs):
    user = getCurrentUser()
    if user:
      if checkAuthority("item",user):
        return handler(request,*args,**kargs)
      else:
        return authorityError(request,"Not authorised activity, You need to be in the item modification group to do this")
    else: 
      return loginError(request,"Please login with your google account continue");
  return rst_handler

def authority_ebay(handler):
  def rst_handler(request,*args,**kargs):
    user = getCurrentUser()
    if user:
      if checkAuthority("ebay",user):
        return handler(request,*args,**kargs)
      else:
        return authorityError(request,"Not authorised activity, You need to be in the ebay management group to do this")
    else:
      return loginError(request,"Please login with your google account continue");
  return rst_handler

def authority_config(handler):
  def rst_handler(request,*args,**kargs):
    user = getCurrentUser()
    if user:
      if checkAuthority("config",user):
        return handler(request,*args,**kargs)
      else:
        return authorityError(request,"Not authorised activity, You need to be in the site configuration group to do this")
    else:
      return loginError(request,"Please login with your google account continue");
  return rst_handler

