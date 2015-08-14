import django.core.handlers.wsgi
import logging
from django.template import loader,Context,RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from ebaysdk import finding
from ebaysdk.exception import ConnectionError
from ebayapi.api import *
from retail import Supplier,ShopInfo,getSupplierFromEbayInfo
import retailtype
from google.appengine.api import users
from error import *
from lxml import etree 
import urllib, random, json, datetime
import zuser
from StringIO import StringIO

def getEbayInfo(request): 
  token = getToken(request)
  if ('ebayinfo' in request.session):
    return request.session.get('ebayinfo',{})
  else:
    return {}

def ebay_ajax_prefix(handler):
  def rst_handler(request,*args,**kargs):
    token = getToken(request)
    if token:
      ebayinfo = getEbayInfo(request)
      return handler(ebayinfo,*args,**kargs)
    else:
      return returnError("Not authorised")
  return rst_handler

def ebay_view_prefix(handler):
  def rst_handler(request,*args,**kargs):
    token = getToken(request)
    if token:
      ebayinfo = getEbayInfo(request)
      return handler(request,*args,**kargs)
    else:
      context = Context({})
      return (render_to_response("ebaylogin.html",context,context_instance=RequestContext(request)))
  return rst_handler

def GetXSLT(xslt_context,xslt_template):
  xslt_template = loader.get_template(xslt_template)
  xslt_str = xslt_template.render(xslt_context)
  xslt_doc = etree.parse(StringIO(xslt_str))
  xslt = etree.XSLT(xslt_doc)
  return xslt

def checkSuccess(doc):
  ack = doc.xpath("//xs:Ack",
    namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
  if('Success' in ack.text):
    return True;
  else:
    return False;

def getItem(itemid,token):
  item = GetItem(itemid,token)
  xml_doc = etree.parse(StringIO(item))
  ack = xml_doc.xpath("//xs:Ack",
    namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
  if('Success' in ack.text):
    title = xml_doc.xpath("//xs:Title",
      namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
    price = xml_doc.xpath("//xs:ConvertedCurrentPrice",
      namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
    return {'label':title,'value':price}
  else:
    return None
  return None

# We will save the referrer so that we can route back

def auth(request):
  # We first need to check whether this session is already linked to some ebay shop or not.
  token = getToken(request)
  if token:
    return HttpResponseRedirect('/admin/')
  else:
    if ('HTTP_REFERER' in request.META):
      request.session['continue'] = request.META['HTTP_REFERER']
    sessionid = GetSessionID(request)
    xml_doc = etree.parse(StringIO(sessionid))
    ack = xml_doc.xpath("//xs:Ack",
    namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
    if('Success' in ack.text):
      session = xml_doc.xpath("//xs:SessionID",
        namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
      ebayinfo = request.session.get('ebayinfo',{})
      ebayinfo['session'] = session.text
      request.session['ebayinfo'] = ebayinfo
      args = urllib.quote_plus("zre="+request.META['HTTP_HOST']) 
      token = GetToken(args,session.text)
      return token
    else:
      return HttpResponse(sessionid)

def logoutebay(request):
  request.session['ebayinfo'] = None
  return HttpResponseRedirect('/admin/')

def authsuccess(request):
  return HttpResponseRedirect('http://' + request.GET['zre'])

def authfail(request):
  return HttpResponseRedirect('http://' + request.GET['zre'])

# This private function gets the ebay token if it exists in the current session. It will try fetch one if ebay is connected. It returns None if failed to get a token.

def getToken(request):
  if (not 'ebayinfo' in request.session) or (not request.session['ebayinfo']):
    request.session['ebayinfo'] =  {}
  ebayinfo = request.session.get('ebayinfo',{})
  user = users.get_current_user()

# we are going to fetch the token if it does not exist yet
  token = ""
  if (('token' in ebayinfo) and (ebayinfo['token'])):
    token = ebayinfo['token']
  else:
    if ('session' in ebayinfo): 
      token = FetchToken(request,ebayinfo['session'])
      xml_doc = etree.parse(StringIO(token))
      ack = xml_doc.xpath("//xs:Ack",
        namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
      if('Success' in ack.text):
        token = xml_doc.xpath("//xs:eBayAuthToken",
          namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
        token = token.text
      else:
        msg = xml_doc.xpath("//xs:LongMessage",
        namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
        ebayerror = msg.text
        ebayinfo['error'] = ebayerror
        # should not update ebayinfo in request.session
        # request.session['ebayinfo'] = ebayinfo
        logging.info("Can not get token from ebay id:" + token)
        return None
    elif user:
      usr = zuser.getUser(user.email(),True)
      if (usr and usr.ebaytoken):
        ebayinfo['token'] = usr.ebaytoken
    else:
      logging.info("Can not get session for ebay auth")
      return None
# By the above computation we have tried to get the token
  ebayinfo['token'] = token

# so far we might need to update the token of the current user 
  if user:
    usr = zuser.getUser(user.email(),False)
    if (usr):
      usr.ebaytoken = token
      usr.put()

  logging.info("ebayinfo:" + json.dumps(ebayinfo))
  if ('token' in ebayinfo) and ebayinfo['token']: 
    request.session['ebayinfo'] = ebayinfo

# here we try to get as much info as possible from a ebay token
    if((not 'id' in ebayinfo) or (not 'email' in ebayinfo)):
      user = GetUserInfo(token)
      user_doc = etree.parse(StringIO(user))
      ack = user_doc.xpath("//xs:Ack",
        namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
      if ('Success' in ack.text):
        email = user_doc.xpath("//xs:Email",
          namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
        ebayinfo['email'] = email.text
        uid = user_doc.xpath("//xs:UserID",
          namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
        ebayinfo['id'] = uid.text
      else:
        request.session['ebayinfo'] = {}
        logging.info("Can not find email address in ebayinfo")
        return None
    if((not 'store' in ebayinfo) or (not 'logo' in ebayinfo) or (not 'category' in ebayinfo)):
      store = GetStore(token)
      store_doc = etree.parse(StringIO(store))
      ack = store_doc.xpath("//xs:Ack",
        namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
      if ('Success' in ack.text):
        name = store_doc.xpath("//xs:Store/xs:Name",
          namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
        ebayinfo['store'] = name.text
        logo = store_doc.xpath("//xs:Store/xs:Logo/xs:URL",
          namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
        ebayinfo['logo'] = logo.text
        cgs = {}
        categories = store_doc.xpath("//xs:Store/xs:CustomCategories/xs:CustomCategory",
          namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})
        a = etree.tostring(categories[0])
        for category in categories:
          name = category.xpath("./xs:Name",
            namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
          id = category.xpath("./xs:CategoryID",
            namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
          cgs[id] = {'name':name,'children':{}}
          childcategories = category.xpath("./xs:ChildCategory",
            namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})
          for child in childcategories:
            name = child.xpath("./xs:Name",
              namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
            cid = child.xpath("./xs:CategoryID",
              namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
            cgs[id]['children'][cid] = {'name':name}
        ebayinfo['categories'] = cgs
      else:
        request.session['ebayinfo'] = {}
        logging.info("Can not find shopinfo in ebayinfo:" + store)
        return None
    request.session['ebayinfo'] = ebayinfo
    return ebayinfo['token']
  else:
    return None  

####
# This function will append general infomation after item description
# It will replace everything after <!-- below is embed code --> tag
####
@ebay_view_prefix
def ebayorders(request):
  token = getToken(request) 
  tt = datetime.datetime.utcnow()
  ft = tt - datetime.timedelta(hours=24)
  tt = tt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
  ft = ft.strftime("%Y-%m-%dT%H:%M:%S.000Z")
  xml_doc = GetOrders(token,ft,tt)
  xml_doc = etree.parse(StringIO(xml_doc))
  xslt = GetXSLT(Context({}),'xslt/OrdersTable.xslt')
  rst = etree.tostring(xslt(xml_doc.getroot()))
  context = Context({"ORDERS":rst})
  return (render_to_response("ebayorders.html",context,context_instance=RequestContext(request)))

@ebay_view_prefix
def ebayordersajax(request):
  token = getToken(request) 
  year = request.GET['year']
  month = request.GET['month']
  day = request.GET['day']
  tt = datetime.datetime(year=int(year),month=int(month),day=int(day))
  ft = tt - datetime.timedelta(hours=24)
  tt = tt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
  ft = ft.strftime("%Y-%m-%dT%H:%M:%S.000Z")
  xml_doc = GetOrders(token,ft,tt)
  xml_doc = etree.parse(StringIO(xml_doc))
  xslt = GetXSLT(Context({}),'xslt/OrdersTable.xslt')
  rst = etree.tostring(xslt(xml_doc.getroot()))
  return HttpResponse(rst)



####
# This function will append general infomation after item description
# It will replace everything after <!-- below is embed code --> tag
####
def format(ebayinfo,itemid):
  token = ebayinfo['token']
  id = ebayinfo['id']
  config = {'SELLER_ID':id}
  item = GetItem(itemid,token)
  xml_doc = etree.parse(StringIO(item))
  ack = xml_doc.xpath("//xs:Ack",
    namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
  if('Success' in ack.text):
    description = xml_doc.xpath("//xs:Description",
      namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
    refid = xml_doc.xpath("//xs:SKU",
      namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})
    if (not refid):
      return returnError('SKU Not Provided')
    else:
      refid = refid[0].text
#   refid = xml_doc.xpath("//xs:ItemID",
#     namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
    name = xml_doc.xpath("//xs:Title",
      namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
    price = xml_doc.xpath("//xs:ConvertedCurrentPrice",
      namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
    galleryurl = xml_doc.xpath("//xs:GalleryURL",
      namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
    infourl = xml_doc.xpath("//xs:ViewItemURL",
      namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
    ebaycategory = xml_doc.xpath("//xs:PrimaryCategory/xs:CategoryID",
      namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
    category = xml_doc.xpath("//xs:StoreCategoryID",
      namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
    sndcategory = xml_doc.xpath("//xs:StoreCategory2ID",
      namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
    sellingstatus = xml_doc.xpath("//xs:SellingStatus/xs:ListingStatus",
      namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
    topd = description.text.split("<!-- below is embeded code -->")
    config['INITIAL'] = topd[0]
    config['EXTRA'] = ShopInfo.all().filter("type =","ebay").order("name")
# save the item
    iteminfo = {'refid':refid,'name':name
      ,'price':float(price),'cost':float(price),'galleryurl':galleryurl
      ,'infourl':infourl,'category':category,'sndcategory':sndcategory
      ,'description':topd[0],'ebayid':itemid,'ebaycategory':ebaycategory
      ,'specification':"{}"}
    item = retailtype.getItem(refid)
    supplier = getSupplierFromEbayInfo(ebayinfo)
    if item:
      iteminfo['specification'] = item.specification
      # FIXME: We do not update galleryurl back to ebay gallery url at the moment.
      # iteminfo['galleryurl'] = item.galleryurl
      item.ebayid = itemid
      supplier = item.parent()
    zitem = supplier.saveItem(iteminfo)

    config['ITEM'] = zitem
    format = loader.get_template("format.html")
    content = format.render(Context(config))
    if (sellingstatus != "Completed"):
      revise = ReviseItemSimple(item,token,content)
      return (HttpResponse(revise,mimetype = "text/xml"),item)
    else:
      revise = RelistItemSimple(item,token,content)
      xml_doc = etree.parse(StringIO(revise))
      ack = xml_doc.xpath("//xs:Ack",
        namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
      if('Success' in ack.text):
        refid = xml_doc.xpath("//xs:ItemID",
          namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
        zitem.refid = refid
        zitem.put()
      return (HttpResponse(revise,mimetype = "text/xml"),item)
  else:
    return (returnError(item),item)

####
# This function will append general infomation after item description
# It will replace everything after <!-- below is embed code --> tag
####
def sync(ebayinfo,item):
  token = ebayinfo['token']
  id = ebayinfo['id']
  config = {'SELLER_ID':id}
  description = item.description
  name = item.name 
  config['INITIAL'] = description
  config['ITEM'] = item
  config['EXTRA'] = ShopInfo.all().filter("type =","ebay").order("name")
  format = loader.get_template("format.html")
  content = format.render(Context(config))
  if (not item.ebayid):
    revise = ReviseItemBySKU(item.refid,name,token,content)
  else:
    revise = ReviseItem(item,token,content)
  return HttpResponse(revise,mimetype = "text/xml")


def getactivelist(request):
  token = getToken(request)
  page = 1 
  if ("page" in request.GET):
    page = int(request.GET['page'])
  xml_doc = None
  if token:
    if 'itemid' in request.GET:
      rid = request.GET['itemid']
      iteminfo = GetItem(rid,token)
      xml_doc = etree.parse(StringIO(iteminfo))
      xslt = GetXSLT(Context({}),'xslt/MyeBaySelling.xslt')
      list_content = etree.tostring(xslt(xml_doc.getroot()))
    else:
      my_ebay_selling = GetMyeBaySelling(token,page)
      xml_doc = etree.parse(StringIO(my_ebay_selling))
      total = xml_doc.xpath("//xs:TotalNumberOfPages",namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0]
      total = int(total.text);
      xslt = GetXSLT(Context({'pages':range(total+1)[1:]}),'xslt/MyeBaySelling2.xslt')
      list_content = etree.tostring(xslt(xml_doc.getroot()))
    return list_content
  else:
    return None

def getinactivelist(request):
  token = getToken(request)
  page = 1 
  if ("page" in request.GET):
    page = int(request.GET['page'])
  xml_doc = None
  if token:
    if 'itemid' in request.GET:
      rid = request.GET['itemid']
      iteminfo = GetItem(rid,token)
      xml_doc = etree.parse(StringIO(iteminfo))
      xslt = GetXSLT(Context({}),'xslt/MyeBaySelling.xslt')
      list_content = etree.tostring(xslt(xml_doc.getroot()))
    else:
      my_ebay_selling = GetMyeBaySellingInactive(token,page)
      xml_doc = etree.parse(StringIO(my_ebay_selling))
      total = xml_doc.xpath("//xs:TotalNumberOfPages",namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})
      list_content = "" #none item if there is no TotalNumberOfPages provided
      if(total):
        total = int(total.text);
        xslt = GetXSLT(Context({'pages':range(total+1)[1:]}),'xslt/MyeBaySelling2.xslt')
        list_content = etree.tostring(xslt(xml_doc.getroot()))
    return list_content
  else:
    return None


@ebay_view_prefix
def fetchcategory(request):
  query = request.GET['term']
  token = getToken(request)
  rslt = GetCategories(request,token,query)
  xml_doc = etree.parse(StringIO(rslt))
  suggests = xml_doc.xpath("//xs:SuggestedCategory",namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})
  items = []
  for suggest in suggests:
    id = suggest.xpath("./xs:Category/xs:CategoryID",namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
    label = suggest.xpath("./xs:Category/xs:CategoryName",namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
    label = [label]
    parents = suggest.xpath("./xs:Category/xs:CategoryParentName",namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})
    for parent in parents:
       label.append(parent.text)
    label = "->".join(label)
    items.append({'label':label,'value':id})
  return HttpResponse(json.dumps(items),mimetype="text/plain")

  
 
