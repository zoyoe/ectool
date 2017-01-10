import requests,json,datetime,random
import django.core.handlers.wsgi
from django.core.context_processors import csrf
from django.template import loader,Context,RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

import ebayapi.ebay error receipt
from core import userapi

from google.appengine.ext import db
from google.appengine.api import urlfetch, search

"""
FIXME: A very rough implementation of adding something into your cart 
"""
def __get_cart(request):
  cart = request.session.get('cart',{})
  if not cart:
    cart = {}
  return cart

def __set_cart(request,cart):
  request.session['cart'] = cart

def get(request):
  cart = request.session.get('cart',{})
  if not cart:
    cart = {}
  temp_path = currentSite().getTemplate("cartdisplay.html");
  temp = loader.get_template(temp_path)
  context = Context({'CART':cart.values()})
  content = temp.render(context)
  return HttpResponse(content,mimetype = "text/xml")

"""
FIXME: We need to change this into a json type response
"""
def add(request):
  item = request.GET['id']
  token = ebay.getToken(request)
  value = ""
  if (not value in request.GET) or (not 'description' in request.GET):
    iteminfo = Item.getItemByRID(item)
    if (not iteminfo):
      return HttpResponse(status=201)
    dscp = iteminfo.name
    value = iteminfo.price
  else:
    value = request.GET['value']
    dscp = request.GET['description']
  cart = __get_cart(request)
  if item in cart:
    cart[item] = {"id":item,"description":dscp,"price":value,'amount':cart[item]['amount']+1,"galleryurl":cart[item]['galleryurl']}
  else:
    itemobj = Item.getItemByRID(item)
    g = itemobj.galleryurl
    galleryurl = itemobj.galleryurl
    cart[item] = {"id":item,"description":dscp,"price":value,'amount':1,"galleryurl":galleryurl}
  __set_cart(request,cart)
  temp_path = currentSite().getTemplate("cart.thingy");
  temp = loader.get_template(temp_path)
  context = Context({'CART':cart.values()})
  content = temp.render(context)
  return HttpResponse(content,mimetype = "text/xml")

"""
FIXME: We need to change this into a json type response
""" 
def remove(request,item):
  cart = __get_cart(request)
  if item in cart:
    del cart[item]
  __set_cart(request,cart)
  temp_path = currentSite().getTemplate("cart.thingy");
  temp = loader.get_template(temp_path)
  context = Context({'CART':cart.values()})
  content = temp.render(context)
  return HttpResponse(content,mimetype = "text/xml")

