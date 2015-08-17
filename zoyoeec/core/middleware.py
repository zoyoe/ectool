from google.appengine.api import namespace_manager, users
from error import *
class NSMiddleware(object):
  def process_request(self, request):
    try:
      ## if it is not from google appspot, it is a normal web visit
      if (request.META['HTTP_HOST']!="zoyoeec.appspot.com"):
        if (request.META['HTTP_HOST']=="trial.zoyoe.com"):
          ## if it is on trial domain, we set the namespace to be the user email address
          usr = users.get_current_user()
          if (usr):
            namespace_manager.set_namespace(usr.email())
          else:
            return authorityError(request,"Not authorised activity, You need login to start trial")
        else:
          namespace_manager.set_namespace(request.META['HTTP_HOST'])
      else:
        if "ns" in request.GET:
          namespace_manager.set_namespace(request.GET['ns'])
    except:
      pass
    return

  def process_response(self, request, response):        
    return response
