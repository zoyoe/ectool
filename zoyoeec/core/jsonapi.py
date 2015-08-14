import django.core.handlers.wsgi
from django.core.context_processors import csrf
from django.template import loader,Context,RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from ebaysdk import finding
from ebaysdk.exception import ConnectionError
from error import *
from receipt import *
from page import *
import ebay, random
import requests,json,datetime
from google.appengine.ext import db,search
from google.appengine.api import urlfetch
from zuser import *
from retailtype import getCategoryItems, getItem

def categories(request):
  stories = siteinfo()
  response =  HttpResponse(json.dumps(stories))
  response['Access-Control-Allow-Origin']  = "*"
  return response

def item(request,itemid):
  stories = siteinfo()
  item = getItem(itemid)
  if item:
    iteminfo = {}
    iteminfo['galleryurl'] = item.galleryurl
    iteminfo['description'] = item.description
    iteminfo['specification'] = item.specification
    iteminfo['infourl'] = "/admin/item/"+item.parent().name+"/"+str(item.key().id()) +"/"
    response =  HttpResponse(json.dumps(iteminfo))
    response['Access-Control-Allow-Origin']  = "*"
    return response
  else:
    response =  HttpResponse("{}")
    response['Access-Control-Allow-Origin']  = "*"
    return response

def items(request,category):
  query = getCategoryItems(category)
  myPagedQuery = PagedQuery(query, 48)
  items = []
  dict = {}
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
    dict['queryurlprev'] = idx-1
  if (idx < len(dict['pages'])):
    dict['queryurlnext'] = idx+1
  dict['sellitems'] = []
  for item in items:
    dict['sellitems'].append({'name':item.name,
      'galleryurl':item.galleryurl,'price':item.price,'refid':item.refid,'category':item.category});
  response =  HttpResponse(json.dumps(dict))
  response['Access-Control-Allow-Origin']  = "*"
  return response




