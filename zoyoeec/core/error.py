from django.template import loader,Context,RequestContext
from django.http import HttpResponse
from retailtype import *
from StringIO import StringIO

def formatName(name):
  return name.replace(" ", "_")

def xmlError(error):
  return HttpResponse("<?xml version='1.0' encoding='utf-8'?><ZoyoeError>" + error + "</ZoyoeError>",mimetype="text/xml")

def ZoyoeError(error):
  return HttpResponse("<?xml version='1.0' encoding='utf-8'?><ZoyoeError>" + error + "</ZoyoeError>",mimetype="text/xml")

def ZoyoeSuccess(success):
  return HttpResponse("<?xml version='1.0' encoding='utf-8'?><ZoyoeSuccess>" + success + "</ZoyoeSuccess>",mimetype="text/xml")

def retailError(request,error,url="/retail/receiptview/"):
  stories = getCategoriesInfo()
  context = Context({'ERROR':error,'URL':url,'STORIES':stories})
  temp_path = currentSite().getTemplate("error.html");
  return (render_to_response(temp_path
    ,context,context_instance=RequestContext(request)))

def userError(request,error):
  stories = getCategoriesInfo()
  context = Context({'ERROR':error,'STORIES':stories})
  return (render_to_response("usererror.html"
    ,context,context_instance=RequestContext(request)))

def loginError(request,error):
  stories = getCategoriesInfo()
  context = Context({'ERROR':error,'STORIES':stories})
  return (render_to_response("error/loginerror.html"
    ,context,context_instance=RequestContext(request)))

def authorityError(request,error):
  stories = getCategoriesInfo()
  context = Context({'ERROR':error,'STORIES':stories})
  return (render_to_response("error/authorityerror.html"
    ,context,context_instance=RequestContext(request)))


# We put the latest error in the session. 
# However this is might cause problems when 2 instance are created at the same time.
def builderror(request,error):
  request.session['error'] = error


def chain(deco):
  def new_decorator(deco_input):
    def rslt(handler):
      def rslt_handler(request,*args,**kargs):
        return (deco(deco_input(handler)))(request,*args,**kargs)
      return rslt_handler
    return rslt
  return new_decorator
    
    
