from django.template import loader,Context,RequestContext
from django.http import HttpResponse
from lxml import etree
from retailtype import *
from StringIO import StringIO

def returnError(error):
  return HttpResponse("<?xml version='1.0' encoding='utf-8'?><ZoyoeError>" + error + "</ZoyoeError>",mimetype="text/xml")


def ZoyoeSuccess(success):
  return HttpResponse("<?xml version='1.0' encoding='utf-8'?><ZoyoeSuccess>" + success + "</ZoyoeSuccess>",mimetype="text/xml")

def retailError(request,error,url="/retail/receiptview/"):
  stories = getCategoriesInfo()
  context = Context({'ERROR':error,'URL':url,'STORIES':stories})
  temp_path = currentsite().gettemplate("error.html");
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
