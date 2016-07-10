from google.appengine.api import namespace_manager, users
from django.shortcuts import render_to_response
import error
import record
import retailtype
import core.retailtype

class NSMiddleware(object):
  def process_request(self, request):
    try:
      ## if it is not from google appspot, it is a normal web visit
      if (request.META['HTTP_HOST']!="zoyoeec.appspot.com"):
        namespace_manager.set_namespace(request.META['HTTP_HOST'])
      else:
        if "ns" in request.GET:
          namespace_manager.set_namespace(request.GET['ns'])
    except:
      pass
    return

  def process_response(self, request, response):        
    return response


def info(request):
  extra = retailtype.ShopInfo.all().filter("type =","footer")
  analytic = retailtype.ShopInfo.all().filter("name =","analytic").get()
  if analytic:
    analytic = analytic.content
  logourl = retailtype.ShopInfo.all().filter("name =","logo").get()
  if logourl:
    logourl = logourl.content
  history = record.getItemHistory(request)
  error = request.session.get('error')
  request.session['error'] = None

  # Collect information of cart
  cart = request.session.get('cart',{})
  if not cart:
    cart = {}

  return {'CART':cart.values(),'HISTORY':history, 'ERROR':error, 'FOOTER':extra,'ANALYTIC':analytic,'LOGO':logourl}