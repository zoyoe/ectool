from django.template import loader,Context,RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response
from google.appengine.ext import db
import random,json
import error,retailtype
from google.appengine.api import users
from google.appengine.api import namespace_manager

from lxml import etree
import cryptohelper

def user_pre_processor(request):
  user = getCurrentUser(request)
  return {'user':user}

class UserInfo(db.Model):
  email = db.StringProperty(default='xgao@zoyoe.com')
  ebaytoken = db.TextProperty(default=None)
  authtoken = db.StringProperty(default="[]")
  history = db.TextProperty(default="{}")
  password = db.TextProperty(default="")
  oauth = db.BooleanProperty(default=False)
  def addAuthority(self,tokens):
    totauth = json.loads(self.authtoken)
    totauth = totauth + tokens
    self.authtoken = json.dumps(totauth)
    self.put()

def __get_user(email,createifnotexist = False):
  user = UserInfo.all().filter("email =",email).get()
  if (not user and createifnotexist):
    user = UserInfo(email = email)
    user.put()
  return user

def getCurrentUser(request):
  user = users.get_current_user()
  if user:
    user =  __get_user(user.email(),True)
    if (user and user.oauth == False):
      user.oauth = True
      user.put()
    return user
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
      pw = cryptohelper.decrypt(email,user.password)
      if pw != password:
        user = None
      else:
        request.session["email"] = email
    else:
      user = None
    return user

def registerUser(request,email,password):
    user = __get_user(email)
    if user:
      return None
    else:
      user = __get_user(email,True)
      user.password = cryptohelper.encrypt(email,password)
      user.put()
    return user

def logoutUser(request):
  user = users.get_current_user()
  if user:
    return None
  else:
    user = getCurrentUser(request)
    request.session["email"] = None
    return user

def checkAuthority(authority,user):
  if not user:
    return False
  totauth = json.loads(user.authtoken)
  if (any(authority in s for s in totauth)):
    return True
  else:
    return False

def redirect_login(request):
  absoluteurl = request.build_absolute_uri()
  return HttpResponseRedirect("/login/?requesturl=" + crptyhelper.encrypt("url",absoluteurl))



##def ajax_require_work_space


####
#
# Most commonly used prefix before view requests or ajax requests.
#
####

def require_work_space(handler):
  def rst_handler(request, *args, **kargs):
    site = retailtype.currentSite()
    if site:
      return handler(request,*args,**kargs)
    else:
      return error.workspaceError(request,"work space not exist")
  return rst_handler


@error.chain(require_work_space)
def require_login(handler):
  def rst_handler(request,*args,**kargs):
    site = retailtype.currentSite()
    if site and site.requirelogin:
      user = getCurrentUser(request)
      if not user:
        return error.loginError(request, "login required")
    return handler(request,*args,**kargs)
  return rst_handler

@error.chain(require_work_space)
def authority_login(handler):
  def rst_handler(request,*args,**kargs):
    user = getCurrentUser(request)
    if not user:
      return error.loginError(request, "login required")
    return handler(request,*args,**kargs)
  return rst_handler


@error.chain(authority_login)
def authority_item(handler):
  def rst_handler(request,*args,**kargs):
    user = getCurrentUser(request)
    if user:
      if checkAuthority("item",user):
        return handler(request,*args,**kargs)
      else:
        return error.authorityError(request,"Not authorised activity, You need to be in the item modification group to do this")
    else: 
      return redirect_login(request)
  return rst_handler

@error.chain(authority_login)
def authority_ebay(handler):
  def rst_handler(request,*args,**kargs):
    user = getCurrentUser(request)
    if user:
      if checkAuthority("ebay",user):
        return handler(request,*args,**kargs)
      else:
        return error.authorityError(request,"Not authorised activity, You need to be in the ebay management group to do this")
    else:
      return redirect_login(request)
  return rst_handler

@error.chain(authority_login)
def authority_config(handler):
  def rst_handler(request,*args,**kargs):
    user = getCurrentUser(request)
    if user:
      if checkAuthority("config",user):
        return handler(request,*args,**kargs)
      else:
        return error.authorityError(request,"Not authorised activity, You need to be in the site configuration group to do this")
  return rst_handler



