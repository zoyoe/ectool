from google.appengine.api import namespace_manager, users
from django.shortcuts import render_to_response
from error import *
import retailtype
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
