# Create your views here.
from core.inc import *
import api
from StringIO import StringIO
import HTMLParser

htmlparser = HTMLParser.HTMLParser()

# NOTICE: This is the top level module, do not import this file.

def activelist(request):
  my_ebay_selling = api.GetMyeBaySelling()
  xml_doc = etree.parse(StringIO(my_ebay_selling))
  xslt = GetXSLT(Context({}),'xslt/MyeBaySelling.xslt')
  list_content = etree.tostring(xslt(xml_doc.getroot()))
  temp = loader.get_template('views/activelist.html')
  c = Context({'list_content':list_content})
  response = HttpResponse(temp.render(c),mimetype = "text/html")
  return response

def item(request,item_id):
  item_str = api.GetItem(item_id)
  xml_doc = etree.parse(StringIO(item_str))
  xslt_detail = GetXSLT(Context({}),'xslt/Item.xslt')
  detail = etree.tostring(xslt_detail(xml_doc.getroot()))
  xslt_description = GetXSLT(Context({}),'xslt/Description.xslt')
  description = htmlparser.unescape(etree.tostring(xslt_description(xml_doc.getroot())))
  temp = loader.get_template('views/item.html')
  view_item_url = xml_doc.xpath("//xs:ViewItemURL",
    namespaces={'xs':"urn:ebay:apis:eBLBaseComponents"})[0].text
  c = Context({'item_id':item_id,'detail':detail,
    'view_item_url':view_item_url,
    'description':description})
  response = HttpResponse(temp.render(c),mimetype = "text/html")
  return response

def info(request):
  rq = request.REQUEST
  dict = {}
  dict['TITLE'] = rq['title'] if rq.has_key('title') else None
  dict['QUANTITY'] = rq['quantity'] if rq.has_key('quantity') else None
  dict['MEASURE'] = rq['measurement'] if rq.has_key('measurement') else None
  dict['SHIPPING'] = rq['shipping'] if rq.has_key('shipping') else None
  dict['PAYMENT'] = rq['payment'] if rq.has_key('payment') else None
  dict['TITLE'] = rq['title'] if rq.has_key('title') else None
  dict['ICON1'] = rq['icon1'] if rq.has_key('icon1') else None
  dict['ICON2'] = rq['icon2'] if rq.has_key('icon2') else None
  dict['ICON3'] = rq['icon3'] if rq.has_key('icon3') else None
  dict['ICON4'] = rq['icon4'] if rq.has_key('icon4') else None
  dict['ICON5'] = rq['icon5'] if rq.has_key('icon5') else None
  dict['ICON6'] = rq['icon6'] if rq.has_key('icon6') else None
  return dict
