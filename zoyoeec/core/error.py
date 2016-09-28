from django.template import loader,Context,RequestContext
from django.http import HttpResponse
from retailtype import *
from StringIO import StringIO
from lxml import etree

def formatName(name):
  return name.replace(" ", "_")

def xmlError(error,extradoc = None):
  xstr = "<?xml version='1.0' encoding='utf-8'?><ZoyoeError>" + error + "</ZoyoeError>"
  if extradoc:
    xdoc = etree.parse(StringIO(xstr))
    xdoc.getroot().appendChild(extradoc.getroot())
    xstr = etree.tostring(xdoc, pretty_print=True)
  return HttpResponse(xstr, mimetype="text/xml")

def xmlSuccess(success,extradoc = None):
  xstr = "<?xml version='1.0' encoding='utf-8'?><ZoyoeSuccess>" + success + "</ZoyoeSuccess>"
  if extradoc:
    xdoc = etree.parse(StringIO(xstr))
    xdoc.getroot().appendChild(extradoc.getroot())
    xstr = etree.tostring(xdoc, pretty_print=True)
  return HttpResponse(xstr, mimetype="text/xml")


####
#
# Usually we do not append extra document in which case it returns a pure zoyoe error or success xml document
#
####

def ZoyoeError(error):
  return xmlError(error)

def ZoyoeSuccess(success):
  return xmlSuccess(success)

####
#
# plain error which are html pages
#
####

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


####
#
# We put the latest error in the session. 
# However this is might cause problems when 2 instance are created at the same time.
#
####
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
    

