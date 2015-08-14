from google.appengine.api import namespace_manager
class NSMiddleware(object):
  def process_request(self, request):
    try:
      if (request.META['HTTP_HOST']!="zoyoeec.appspot.com"):
        namespace_manager.set_namespace(request.META['HTTP_HOST'])
      else:
        if "ns" in request.GET:
          namespace_manager.set_namespace(request.GET['ns'])
        else:
          namespace_manager.set_namespace("habitania.zoyoe.com")
    except:
      pass
    return

  def process_response(self, request, response):        
    return response
