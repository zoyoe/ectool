import django.core.handlers.wsgi
from django.core.context_processors import csrf
from django.template import loader,Context,RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
from google.appengine.ext import db
import random,json
from retailtype import *
from google.appengine.api import users

def user(request):
  user = users.get_current_user()
  return {'user':user}

def info(request):
  extra = ShopInfo.all().filter("type =","footer")
  analytic = ShopInfo.all().filter("name =","analytic").get()
  if analytic:
    analytic = analytic.content
  logourl = ShopInfo.all().filter("name =","logo").get()
  if logourl:
    logourl = logourl.content
  return {'FOOTER':extra,'ANALYTIC':analytic,'LOGO':logourl}
