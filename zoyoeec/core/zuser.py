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

from Crypto.Cipher import XOR
import base64

def encrypt(key, plaintext):
  cipher = XOR.new(key)
  return base64.b64encode(cipher.encrypt(plaintext))

def decrypt(key, ciphertext):
  cipher = XOR.new(key)
  return cipher.decrypt(base64.b64decode(ciphertext))


class UserInfo(db.Model):
  email = db.StringProperty(default='xgao@zoyoe.com')
  ebaytoken = db.TextProperty(default=None)
  authtoken = db.StringProperty(default="[]")
  history = db.TextProperty(default="{}")

def __get_user(email,createifnotexist = False):
  user = UserInfo.all().filter("email =",email).get()
  if (not user and createifnotexist):
    user = UserInfo(email = email)
    user.put()
  return user

def getCurrentUser(request):
  user = users.get_current_user()
  if user:
    return __get_user(user.email(),True)
  else:
    email = request.session.get("email")
    if email:
      return __get_user(email,False)
    else:
      return None

def loginUser(request,email,password):
  user = getCurrentUser(request)
  if user:
    return user
  else:
    user = __get_user(email)
    if user:
      pw = decrypt(email,user.password)
      if pw == password:
        user = None
      else:
        request.session["email"] = email
    else:
      user = None
    return user

def registerUser(request,email,password)
    user = __get_user(email)
    if user:
      return None
    else:
      user = __get_user(email,True)
      user.password = encrypt(email,password)
      user.put()
    return user

def logoutUser(request):
  user = users.get_current_user()
  if user:
    return None
  else:
    user = getCurrentUser()
    request.session["email"] = None
    return user

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
    user = getCurrentUser(request)
    if user:
      return handler(request,*args,**kargs)
    else:
      return loginError(request,"Please login with your google account continue");
  return rsthandler

def authority_item(handler):
  def rst_handler(request,*args,**kargs):
    user = getCurrentUser(request)
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
    user = getCurrentUser(request)
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
    user = getCurrentUser(request)
    if user:
      if checkAuthority("config",user):
        return handler(request,*args,**kargs)
      else:
        return authorityError(request,"Not authorised activity, You need to be in the site configuration group to do this")
    else:
      return loginError(request,"Please login with your google account continue");
  return rst_handler

