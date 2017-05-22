from django.template import loader,Context,RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
import dbtype, cryptohelper
from StringIO import StringIO
from lxml import etree
import json

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
  
def jsonError(error,msg):
  return jsonReply(error,msg)

def jsonSuccess(msg):
  return jsonReply('success',msg)

####
# 
# Plain error which are html pages.
#
####

def retailError(request,error,url="/"):
  stories = dbtype.getCategoriesInfo()
  context = Context({'ERROR':error,'URL':url,'STORIES':stories})
  temp_path = dbtype.currentSite().getTemplate("error.html");
  return (render_to_response(temp_path
    ,context,context_instance=RequestContext(request)))

def retailErrorAjax(request,error):
  return xmlError(error)

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

"""
@note: This is suppose to be a decorator 
"""
def setAjaxTag(handler):
  def rst_handler(request, *args, **kargs):
    request.reqtype = "ajax"
    return handler(request,*args,**kargs)
  return rst_handler

def isAjaxRequest(request):
  return request.reqtype =='ajax';

"""
@note: This is suppose to be a decorator
"""
def setJSONTag(handler):
  def rst_handler(request, *args, **kargs):
    request.reqtype = "json"
    return handler(request,*args,**kargs)
  return rst_handler

def isJSONRequest(request):
  return request.reqtype =='json';

def workspaceError(request,error):
  if isAjaxRequest(request):
    return xmlError(error)
  elif isJSONRequest(request):
    return jsonError(error)
  else:
    return HttpResponseRedirect("/workspace/")

def loginError(request,error):
  if isAjaxRequest(request):
    return xmlError("login required")
  elif isJSONRequest(request):
    return jsonError("login required")
  else:
    absoluteurl = request.build_absolute_uri()
    return HttpResponseRedirect("/login/?requesturl=" + cryptohelper.encrypt("url",absoluteurl))

def authorityError(request,error):
  if isAjaxRequest(request):
    return xmlError(error)
  elif isJSONRequest(request):
    return jsonError(error)
  else:
    stories = dbtype.getCategoriesInfo()
    context = Context({'ERROR':error,'STORIES':stories})
    return (render_to_response("error/authorityerror.html",context,context_instance=RequestContext(request)))

"""
@attention We put the latest error in the session. 
  However this is might cause problems when 2 instance are created at the same time.
"""
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
