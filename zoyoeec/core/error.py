from django.template import loader,Context,RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
import retailtype, cryptohelper
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

def jsonReply(success, data = {}):
  reply = {'reply': success,'data': data}
  return HttpResponse(json.dumps(reply), mimetype="text")
  


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
# Plain error which are html pages.
#
####

def retailError(request,error,url="/retail/receiptview/"):
  stories = retailtype.getCategoriesInfo()
  context = Context({'ERROR':error,'URL':url,'STORIES':stories})
  temp_path = currentSite().getTemplate("error.html");
  return (render_to_response(temp_path
    ,context,context_instance=RequestContext(request)))

def retailErrorAjax(request,error):
  return ZoyoeError(error)

####
#
# Admin Error
#
###


####
#
# We need some special way to distinguish between view request or ajax request
#
####

def isAjaxRequest(request):
  return False

def workspaceError(request,error):
  if isAjaxRequest(request):
    return zoyoeError(error)
  else:
    return HttpResponseRedirect("/workspace/")

def loginError(request,error):
  if isAjaxRequest(request):
    return zoyoeError("login required")
  else:
    absoluteurl = request.build_absolute_uri()
    return HttpResponseRedirect("/login/?requesturl=" + cryptohelper.encrypt("url",absoluteurl))

def authorityError(request,error):
  if isAjaxRequest(request):
    return ZoyoeError(error)
  else:
    stories = retailtype.getCategoriesInfo()
    context = Context({'ERROR':error,'STORIES':stories})
    return (render_to_response("error/authorityerror.html",context,context_instance=RequestContext(request)))


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
