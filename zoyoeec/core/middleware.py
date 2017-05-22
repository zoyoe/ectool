from google.appengine.api import namespace_manager, users
from django.shortcuts import render_to_response
import error
import record
import dbtype
import core.dbtype

"""
@summary: Requrest type is html by default.
"""
class NSMiddleware(object):
  def process_request(self, request):
    request.reqtype = 'html'
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
  site = dbtype.currentSite()
  history = record.getItemHistory(request)
  error = request.session.get('error')
  request.session['error'] = None
  return {'HISTORY':history, 'SITE':site, 'ERROR':error}
