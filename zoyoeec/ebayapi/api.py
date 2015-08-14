from django.template import Context, loader
from django.http import HttpResponseRedirect
import urllib
import httplib
#httplib.HTTPConnection.debuglevel = 1

# Currently it only supports Australia

AUS_SITE_ID = 15

sandbox = {}
sandbox['dev_id'] = '2ffcd0ee-faff-49cc-b1db-12a2cfb962df'
sandbox['app_id'] = 'zoyoe4cf9-614e-4039-8d36-4fb30acd3e0'
sandbox['cert_id'] = 'f06d6893-34ee-4430-b67a-bfc63b2da824'

product = {}
product['dev_id'] = '2ffcd0ee-faff-49cc-b1db-12a2cfb962df'
product['app_id'] = 'zoyoea269-b772-4c8d-98bb-e8a23cefc0e'
product['cert_id'] = 'ab38bb47-b6c8-4593-bc85-8f02da76b63c'
product['api_host'] = 'api.ebay.com'
product['api_uri'] = '/ws/api.dll'
product['ru_name'] = 'zoyoe-zoyoea269-b772--rxcszk'

current_app  = product

# GetToken function will redirect user to sinin.ebay.com
# which will write a session back as sessionid
def GetToken(args,sessionid):
  return HttpResponseRedirect("http://signin.ebay.com"
    + '/ws/eBayISAPI.dll?SignIn&RuName='
    + current_app['ru_name'] 
    + '&RuParams=' + args
    + '&SessID=' + sessionid)


def CommonHead(call_name,site_id):
  common_head = {}
  common_head['X-EBAY-API-COMPATIBILITY-LEVEL'] = 707 
  common_head['X-EBAY-API-CALL-NAME'] = call_name
  common_head['X-EBAY-API-SITEID'] = site_id
  common_head['Content-Type'] = 'text/xml'
  return common_head

def CommonHeadCurrent(call_name):
  return CommonHead(call_name,AUS_SITE_ID)

def FullHeadCurrent(head):
  head['X-EBAY-API-APP-NAME'] = current_app['app_id']
  head['X-EBAY-API-DEV-NAME'] = current_app['dev_id']
  head['X-EBAY-API-CERT-NAME'] = current_app['cert_id']
  return head

def GetEbayReply(headers,content):
  conn = httplib.HTTPSConnection(current_app['api_host'])
  conn.request("POST",current_app['api_uri'],content,headers)
  response = conn.getresponse()
  data = response.read()
  conn.close()
  return data

def GetMyeBaySelling(token,page):
  xml_template = loader.get_template('GetMyeBaySelling.xml')
  para = {'token':token,'page':page}
  content = xml_template.render(Context(para))
  return GetEbayReply(CommonHeadCurrent('GetMyeBaySelling'),content)

def GetMyeBaySellingInactive(token,page):
  xml_template = loader.get_template('GetMyeBaySellingInactive.xml')
  para = {'token':token,'page':page}
  content = xml_template.render(Context(para))
  return GetEbayReply(CommonHeadCurrent('GetMyeBaySelling'),content)



def GetUserInfo(token):
  xml_template = loader.get_template('GetUser.xml')
  para = {'token':token}
  content = xml_template.render(Context(para))
  return GetEbayReply(CommonHeadCurrent('GetUser'),content)

def GetItem(item_id,token):
  xml_template = loader.get_template('GetItem.xml')
  para = {'token':token,'item_id':item_id}
  content = xml_template.render(Context(para))
  head = CommonHeadCurrent('GetItem')
  return GetEbayReply(head,content)

def GetItemBySKU(sku,token):
  xml_template = loader.get_template('GetItemBySKU.xml')
  para = {'token':token,'sku':sku}
  content = xml_template.render(Context(para))
  head = CommonHeadCurrent('GetItem')
  return GetEbayReply(head,content)

def AddItem(token,item):
  xml_template = loader.get_template('AddItem.xml')
  #xml_template = loader.get_template('VerifyAddFixedPriceItem.xml')
  para = {'token':token,'ITEM':item}
  content = xml_template.render(Context(para))
  #head = CommonHeadCurrent('VerifyAddFixedPriceItem')
  head = CommonHeadCurrent('AddFixedPriceItem')
  return GetEbayReply(head,content)

def GetOrders(token,ft,tt):
  xml_template = loader.get_template('GetOrders.xml')
  para = {'token':token,'from':ft,'to':tt}
  content = xml_template.render(Context(para))
  head = CommonHeadCurrent('GetOrders')
  return GetEbayReply(head,content)
 
def GetStore(token):
  xml_template = loader.get_template('GetStore.xml')
  para = {'token':token}
  content = xml_template.render(Context(para))
  return GetEbayReply(CommonHeadCurrent('GetStore'),content)

def SetUserNotes(item_id,note):
  xml_template = loader.get_template('SetUserNotes.xml')
  para = {'token':current_app['token'],'item_id':item_id,'note':note}
  content = xml_template.render(Context(para))
  return GetEbayReply(CommonHeadCurrent('SetUserNotes'),content)

def ReviseItem(item,token,content):
  xml_template = loader.get_template('ReviseItem.xml')
  para = {}
  para['token'] = token
  para['item'] = item
  para['description'] = content
  content = xml_template.render(Context(para))
  return GetEbayReply(CommonHeadCurrent('ReviseItem'),content)

def ReviseItemSimple(item,token,content):
  xml_template = loader.get_template('ReviseItemSimple.xml')
  para = {}
  para['token'] = token
  para['item'] = item
  para['description'] = content
  content = xml_template.render(Context(para))
  return GetEbayReply(CommonHeadCurrent('ReviseItem'),content)

def RelistItemSimple(item,token,content):
  xml_template = loader.get_template('RelistItemSimple.xml')
  para = {}
  para['token'] = token
  para['item'] = item
  para['description'] = content
  content = xml_template.render(Context(para))
  return GetEbayReply(CommonHeadCurrent('RelistItem'),content)





def ReviseItemBySKU(sku,title,token,desc):
  xml_template = loader.get_template('ReviseItemBySKU.xml')
  para = {}
  para['token'] = token
  para['name'] = title
  para['sku'] = sku
  para['description'] = desc
  content = xml_template.render(Context(para))
  return GetEbayReply(CommonHeadCurrent('ReviseItem'),content)

def GetSessionID(request):
  xml_template = loader.get_template('GetSessionID.xml')
  para = current_app
  content = xml_template.render(Context(para))
  return GetEbayReply(FullHeadCurrent(CommonHeadCurrent('GetSessionID')),content)

def GetCategories(request,token,query):
  #xml_template = loader.get_template('GetCategory.xml')
  xml_template = loader.get_template('GetCategorySuggest.xml')
  para = {}
  para['token'] = token
  para['query'] = query 
  content = xml_template.render(Context(para))
  #return GetEbayReply(CommonHeadCurrent('GetCategories'),content)
  return GetEbayReply(CommonHeadCurrent('GetSuggestedCategories'),content)

def FetchToken(request,session):
  xml_template = loader.get_template('FetchToken.xml')
  para = current_app
  para['session_id'] = session
  content = xml_template.render(Context(para))
  return GetEbayReply(FullHeadCurrent(CommonHeadCurrent('FetchToken')),content)
 
 
