import django.core.handlers.wsgi
from django.core.context_processors import csrf
from django.template import loader,Context,RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from ebaysdk import finding
from ebaysdk.exception import ConnectionError
from error import *
from receipt import *
import ebay, random
import requests,json,datetime
from google.appengine.ext import db,search
from google.appengine.api import urlfetch
from zuser import *


def formatName(name):
  return name.replace(" ", "_")

@require_login
def retail(request):
  stories = getCategoriesInfo()
  fliers = ShopInfo.all().filter("type =","category").order("name")
  context = Context({'STORIES':stories,'FLIERS':fliers})
  cover_path = getSiteInfo().getTemplate("cover.html");
  return (render_to_response(cover_path,context,context_instance=RequestContext(request)))

## FIXME: Dont remember #
def matchjson(request):
  ret = {}
  if ('term' in request.GET):
    iid = request.GET['term'].split(".")
    iid.pop()
    iid = ".".join(iid)
    item = getItem(iid)
    if item:
      ret = {'label':item.key().id(),'rid':item.refid
            ,'supplier':item.parent().name}
  return HttpResponse(json.dumps(ret),mimetype = "text/plain")

def searchjson(request):
  items = []
  if ('term' in request.GET):
    iid = request.GET['term']
    itemlist = Item.all().filter("refid >=",iid+"0").filter("refid <=",iid+"z")
    for item in itemlist:
      items.append({'label':item.name,'value':item.refid,
        'price':item.price,'modify':'/admin/item/'+item.parent().name+"/"+str(item.key().id())+"/"})
    return HttpResponse(json.dumps(items),mimetype = "text/plain")
  return HttpResponse('[]',mimetype = "text/plain")

@zuser.require_login
def searchview(request):
  index = search.Index(name="itemindex")
  items = []
  if 'key' in request.GET:
    key = request.GET['key']
    rslt = index.search(key)
    for doc in rslt:
      item = getItem(doc.doc_id)
      if (item.ebayid != None) and (item.ebayid != ""):
        items.append(item)
  stories = getCategoriesInfo()
  context = Context({'RETAIL': True,'ITEM_WIDTH':'200','STORIES':stories,'sellitems':items})
  temp_path = currentSite().getTemplate("products.html");
  return (render_to_response(temp_path,context,context_instance=RequestContext(request)))



# Following are two helping functions to help encoding price 
class Price:
  price = 0 
  def __init__(self,value):
    self.price = float(value)
  def encode(self):
    return format(self.price,".2f")

def eco(obj):
    if isinstance(obj, Price):
        return obj.encode()
    raise TypeError(repr(obj) + " is not JSON serializable")

def r2i(item):
  return {'name':item.description,'quantity':item.amount,
    'unit_price':{'value':Price(item.price),'currency':"AUD"}}

invoice_template = {
  "merchant_info": {
    "email": "zoyoeproject@gmail.com",
    "first_name": "Xin",
    "last_name": "Gao",
    "business_name": "Zoyoe",
    "phone": {
      "country_code": "61",
      "national_number": "0406819592"
    },
    "address": {
      "line1": "551E King Street.",
      "city": "New Town",
      "state": "NSW",
      "postal_code": "2042",
      "country_code": "AU"
    }
  },
  "payment_term" :{
      "term_type": "NET_45"
  },
  "shipping_info": {
    "first_name": "Xin",
    "last_name": "Gao",
    "business_name": "",
    "address": {
    "line1": "16 Morgan st",
    "city": "Kingsgrove",
    "state": "NSW",
    "postal_code": "2041",
    "country_code": "AU"
    }
  }
}

def buildBillingInfo(email,firstname,lastname):
  return {"email":email,"first_name":firstname,"last_name":lastname}

def buildCreditCart(cardnumber,type,em,ey,cvv,firstname,lastname):
  return {"number":cardnumber
    ,"type":type
    ,"expire_month":em
    ,"expire_year":ey
    ,"cvv2":cvv
    ,"first_name":firstname
    ,"last_name":lastname
    }

def buildPayerObject(request):
  return {"payment_method":"paypal"}
  payment_method = request.POST['payment_method']
  if (payment_method == "paypal"):
    return {"payment_method":"paypal"}
  else:
    cardnumber = request.POST['cardnumber']
    type = request.POST['type']
    em = request.POST["expire_month"]
    ey = request.POST["expire_year"]
    cvv = request.POST['cvv']
    firstname = request.POST['first_name']
    lastname = request.POST['last_name']
    return {"payment_method":"credit_card"
      ,"funding_instruments":[{"credit_card":buildCreditCart(cardnumber,type,em,ey,cvv,firstname,lastname)}]}

def buildTransactionObject(receipt):
  receiptitems = ReceiptItem.all().ancestor(receipt)
  cart = {}
  for item in receiptitems:
    if item.iid in cart:
      cart[item.iid]['amount'] += 1
    else:
      cart[item.iid] = {'currency':'AUD','name':item.description,'price':item.price,'quantity':item.amount}
  items = []
  trans =  {"amount":{
    "total":0.0,
    "currency":"AUD",
    "details":{
       "subtotal":0.0,
       "shipping":0.0
        }
    },
    "description":"pay receipt " + str(receipt.key().id()) + " by paypal"
  }
  for iid in cart.keys():
    trans['amount']['details']['subtotal'] += cart[iid]['quantity']*cart[iid]['price']
    cart[iid]['quantity'] = str(int(cart[iid]['quantity']))
    cart[iid]['price'] = str("{0:.2f}".format(float(cart[iid]['price'])))
    items.append(cart[iid])
  trans['amount']['details']['shipping'] = 10.00
  trans['amount']['total'] = str("{0:.2f}".format(trans['amount']['details']['subtotal'] + trans['amount']['details']['shipping']))
  trans['amount']['details']['subtotal'] = str("{0:.2f}".format(trans['amount']['details']['subtotal']))
  trans['amount']['details']['shipping'] = '10.00'
  trans['item_list'] = {'items':items}
  return trans

def createPayment(request,failurl,receipt):
  pdata = {"intent":"sale",
    "payer" : buildPayerObject(request),
    "transactions" : [buildTransactionObject(receipt)],
    "redirect_urls" : {"return_url": "http://" + request.META['HTTP_HOST'] +"/paypal/accept/"
      ,"cancel_url": failurl
     }
  }
  token = getToken(request)
  conn = httplib.HTTPSConnection("api.paypal.com",timeout=100)
  conn.request("POST","/v1/payments/payment",
    json.dumps(pdata),
    {"content-type": "application/json",
     "Accept": "application/json",
     "authorization": "Bearer "+token,
    })
  resp = conn.getresponse()
  conn.close()
  if (resp.status == 201):
    data = resp.read()
    data = json.loads(data)
    return data
  else:
    a = resp.reason
    b = resp.status
    z = 1/0
    return None

#### Following is paypal invoice api stuff,
#### they are very rough at this stage and need to be moved to other place

"""
FIXME: send a paypal invoice by calling paypal invoice api 
Like other functions that uses paypal api, error handling is missing.
"""
def sendinvoice(request,invoice):
  token = getToken(request)
  conn = httplib.HTTPSConnection("api.paypal.com")
  conn.request("POST","/v1/invoicing/invoices/"+invoice+"/send",
    '',
    {"content-type": "application/json",
     "Accept": "application/json",
     "authorization": "Bearer "+token,
    })
  resp = conn.getresponse()
  conn.close()
  b = resp.status
  if(b == 202):
    return True
  else:
    return False


"""
FIXME: create a paypal invoice by calling paypal invoice api 
Like other functions that uses paypal api, error handling is missing.
"""
def createinvoice(request,invoice):
  token = getToken(request)
  conn = httplib.HTTPSConnection("api.paypal.com")
  conn.request("POST","/v1/invoicing/invoices",
    json.dumps(invoice,default=eco),
    {"content-type": "application/json",
     "Accept": "application/json",
     "authorization": "Bearer "+token,
    })
  resp = conn.getresponse()
  conn.close()
  b = resp.status
  data = resp.read()
  return data


def buildinvoice(receipt,receiptitems):
  invoice = invoice_template
  invoice['billing_info'] = [{"email":receipt.email
    ,"first_name":receipt.firstname
    ,"last_name":receipt.lastname}]
  invoice['items'] = map (r2i,receiptitems)
  invoice['note'] = "zoyoe receipt-id " + str(receipt.key().id()) + "created on " + str(receipt.date)
  invoice['shipping_info'] = {"address":json.loads(receipt.address)
    ,"first_name":receipt.firstname
    ,"lastname":receipt.lastname }
  return invoice

#### end of invoice stuff ####


"""
FIXME: A very rough implementation of adding something into your cart 
"""
def get(request):
  cart = request.session.get('cart',{})
  if not cart:
    cart = {}
  temp_path = currentSite().getTemplate("cartdisplay.html");
  temp = loader.get_template(temp_path)
  context = Context({'CART':cart.values()})
  content = temp.render(context)
  return HttpResponse(content,mimetype = "text/xml")

def add(request):
  item = request.GET['id']
  token = ebay.getToken(request)
  value = ""
  if (not value in request.GET) or (not 'description' in request.GET):
    iteminfo = getItem(item)
    if (not iteminfo):
      return HttpResponse(status=201)
    dscp = iteminfo.name
    value = iteminfo.price
  else:
    value = request.GET['value']
    dscp = request.GET['description']
  cart = request.session.get('cart',{})
  if not cart:
    cart = {}
  if item in cart:
    cart[item] = {"id":item,"description":dscp,"price":value,'amount':cart[item]['amount']+1,"galleryurl":cart[item]['galleryurl']}
  else:
    itemobj = getItem(item)
    g = itemobj.galleryurl
    galleryurl = itemobj.galleryurl
    cart[item] = {"id":item,"description":dscp,"price":value,'amount':1,"galleryurl":galleryurl}
  request.session['cart'] = cart
  temp_path = currentSite().getTemplate("cart.thingy");
  temp = loader.get_template(temp_path)
  context = Context({'CART':cart.values()})
  content = temp.render(context)
  return HttpResponse(content,mimetype = "text/xml")

def remove(request,item):
  cart = request.session.get('cart',{})
  if not cart:
    cart = {}
  if item in cart:
    del cart[item]
  request.session['cart'] = cart
  temp_path = currentSite().getTemplate("cart.thingy");
  temp = loader.get_template(temp_path)
  context = Context({'CART':cart.values()})
  content = temp.render(context)
  return HttpResponse(content,mimetype = "text/xml")

## AJAX --
## FIXME : edit receipt is not well implemeneted
## PLEASE MOVE IT TO RECEIPT module
def editreceipt(request,key):
  receipt = Receipt.get_by_id(int(key))
  receiptitems = ReceiptItem.all().ancestor(receipt)
  cart = {}
  for item in receiptitems:
    if item.iid in cart:
      cart[item.iid]['amount'] += 1
    else:
      cart[item.iid] = {'id':item.iid,'description':item.description,'price':item.price,'amount':item.amount}
  temp = loader.get_template('receipt.html')
  invoice = '{}'
  z = receipt.paypal
  if(receipt.paypal):
    invoice = getinvoice(request,receipt.paypal)
  context = Context({'CART':cart.values(),'RECEIPT':receipt,'INVOICE':json.loads(invoice)})
  content = temp.render(context)
  return HttpResponse(content,mimetype = "text/xml")


# Following are receipt related operators 

# Created a receipt, this is called in save
def createReceipt():
  receipt = Receipt(date = datetime.datetime.now().date())
  receipt.date = datetime.datetime.now().date()
  receipt.put()
  return receipt

def deleteReceipt(key):
  receipt = Receipt.get_by_id(int(key))
  if receipt:
    receipt.delete()
    return True
  else:
    return False
  
### receipt ajax
###
def receipt(request,key):
  receipt = Receipt.get_by_id(int(key))
  receiptitems = ReceiptItem.all().ancestor(receipt)
  cart = {}
  for item in receiptitems:
    if item.iid in cart:
      cart[item.iid]['amount'] += 1
    else:
      cart[item.iid] = {'id':item.iid,'description':item.description,'price':item.price,'amount':item.amount}
  temp = loader.get_template('receipts/receiptinfo-concise.thingy')
  context = Context({'CART':cart.values()})
  content = temp.render(context)
  return HttpResponse(content,mimetype = "text/xml")

def deletereceipt(request,key):
  if(deleteReceipt(key)):
    return ZoyoeSuccess('Receipt deleted')
  else:
    return ZoyoeSuccess('Receipt not found')

@require_login
def checkoutcart(request):
  cart = request.session.get('cart',{})
  request.session['cart'] = {}
  if cart:
    receipt = createReceipt()
    receipt.email = request.POST['email']
    receipt.firstname = request.POST['firstname']
    receipt.lastname = request.POST['secondname']
    receipt.address = json.dumps({
    "line1": request.POST["line1"],
    "city": request.POST["city"],
    "state": request.POST["state"],
    "postal_code":request.POST["postal_code"],
    "country_code": request.POST["country_code"]
    })
    receipt.zuser = getCurrentUser(request)
    for key in cart:
      item = cart[key]
      obj = ReceiptItem(parent=receipt,iid= item['id'],description=item['description'],amount=int(item['amount']),price=float(item['price']))
      obj.date = datetime.datetime.now().date()
      obj.put()
      receipt.total += float(item['price']) * item['amount']
    receipt.put()
    return HttpResponseRedirect('/retail/receiptview/?key='+str(receipt.key().id()))
  else:
    return retailError(request,"Your cart is empty")


## checkout by credit card
#
def expresspaypal(request,key):
  receipt = Receipt.get_by_id(int(key))
  if not receipt:
    return retailError(request,"No Receipt Found with Key: "+key)
  if(receipt.status == "payed"):
    return HttpResponseRedirect('/retail/receiptview/?key='+str(receipt.key().id()))

  failurl = "http://" + request.META['HTTP_HOST'] + '/retail/receiptview/?key=' + str(receipt.key().id())
  data = createPayment(request,failurl,receipt)
  if not data:
    return retailError(request,"Paypal create payment failed!")
  else:
    receipt.status = "paypal-express-" + data['id']
    redirecturl = None
    for link in data['links']:
      if (link['rel'] == "approval_url"):
        redirecturl = link['href']
      if (link['rel'] == "execute"):
        receipt.papal = link['href']
    receipt.put()
    if redirecturl:
      return HttpResponseRedirect(redirecturl)
    return retailError(request,"Pay by paypal failed!")


## approve paypal payment
#
def paypalaccept(request):
  payid = request.GET['paymentId']
  payerid = request.GET['PayerID']
  receipt = Receipt.all().filter("status =","paypal-express-"+payid).get()
  token = getToken(request)
  conn = httplib.HTTPSConnection("api.paypal.com")
  input = {'payer_id':payerid}
  conn.request("POST","/v1/payments/payment/"+payid+"/execute/"
    ,json.dumps(input),
    {"content-type": "application/json",
     "Accept": "application/json",
     "authorization": "Bearer "+token,
    })
  resp = conn.getresponse()
  conn.close()
  data = resp.read()
  if (resp.status == 200):
    data = json.loads(data)
    if data['state'] == "approved":
      receipt.status = "paid"
      receipt.paypal = "express-" + payid
      receipt.put()
      return HttpResponseRedirect('/retail/receiptview/?key='+str(receipt.key().id()))
    else:
      receipt.status = "fail"
      receipt.paypal = "express-" + payid
      receipt.put()
      # should not arrive here !!!
      return retailError(request,"Pay by paypal failed with payment id " + payid)
  else:
    b = resp.status
    c = resp.reason
    # should not arrive here !!!
    return retailError(request,"Pay by paypal failed with payment id " + payid)

## checkout will create an invoice 
# 
def sendpaypalinvoice(request,key):
  receipt = Receipt.get_by_id(int(key))
  if not receipt:
    return retailError(request,"No Receipt Found with Key: "+key)
  if (receipt.paypal != ""):
    return retailError(request,"Paypal of this receipt has already been decided");

  receiptitems = ReceiptItem.all().ancestor(receipt)
  draft = buildinvoice(receipt,receiptitems)
  invoice = createinvoice(request,draft)
  invoice = json.loads(invoice)
  if 'id' in invoice:
    receipt.paypal = "invoice-" + invoice['id']
    receipt.put()
    r = sendinvoice(request,invoice['id'])
    if r:
      return HttpResponseRedirect('/retail/receiptview/?key='+str(receipt.key().id()))
    else:
      return retailError(request,"Paypal invoice created but not send")
  else: 
    return retailError(request,json.dumps(invoice))

## This is not a view function , it is called by used in receipts 
def receiptsearch(request):
  # Here we are going to prepare for the saved billing info
  temp_path = currentSite().getTemplate("receiptsearch.html");
  temp = loader.get_template(temp_path)
  context = Context({})
  content = temp.render(context)
  builderror(request,content)
  return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

@require_login
def receipts(request):
  user = getCurrentUser(request)
  if (user):
      receipts = user.receipt_set
      stories = getCategoriesInfo()
      context = Context({'receipts':receipts,'STORIES':stories})
      temp_path = currentSite().getTemplate("userreceipts.html");
      return (render_to_response(temp_path,context,context_instance=RequestContext(request)))
  else:
      return receiptsearch(request)

@require_login
def receiptview(request):
  receipt = None
  if ('key' in request.GET):
    key = request.GET['key']
    try:
      receipt = Receipt.get_by_id(int(key))
    except ValueError:
      pass
  invoice = None
  if not receipt:
    return retailError(request,"Receipt not exist.")
  if(receipt.paypal and receipt.paypal.startswith("invoice")):
    invoice = getinvoice(request,receipt.paypal.replace("invoice-",""))
  receiptitems = ReceiptItem.all().ancestor(receipt)
  address = json.loads(receipt.address)
  cart = {}
  total = 0
  for item in receiptitems:
    if item.iid in cart:
      cart[item.iid]['amount'] += 1
    else:
      a = item.iid
      stockitem = getItem(item.iid)
      galleryurl = "/static/res/picnotfound.png"
      if (stockitem):
        galleryurl = stockitem.galleryurl
      cart[item.iid] = {'galleryurl':galleryurl,'id':item.iid,'description':item.description,'price':item.price,'amount':item.amount}

  # Here we are going to prepare for the saved billing info
  stories = getCategoriesInfo()
  context = Context({'address':address,'INVOICE':invoice,'RECEIPT':receipt,'STORIES':stories,'CART':cart.values()})
  temp_path = currentSite().getTemplate("receiptview.html");
  return (render_to_response(temp_path
    ,context,context_instance=RequestContext(request)))

@require_login
def billinginfo(request):
  stories = getCategoriesInfo()
  cart = request.session.get('cart',{})
  total = 0.0
  for key in cart:
    item = cart[key]
    total += float(item['price']) * item['amount']
  context = Context({'STORIES':stories,'TOTAL':total,'CART':cart.values()})
  temp_path = currentSite().getTemplate("billinginfo.html");
  return (render_to_response(temp_path
    ,context,context_instance=RequestContext(request)))

def basic_authorization(user, password):
    s = user + ":" + password
    return "Basic " + s.encode("base64").rstrip()

# This private function gets the papal token if it exists in the current session. It will try fetch one if papal is connected. 
# It returns None if failed to get a token.
def getToken(request):
#  if ('papaltoken' in request.session):
#    return request.session['papaltoken']
#  else:
    clientid = "AYrhCwLUvp5zpVHjUpi_aHfFigA0KQJtbFo1iO8APYYoBg8pqWi3Zx6etyCDrirHfP9BsxtaYhgNvXeJ"
    clientid = "Af2WRr1ZdPC-h6F34eDPw8BEtI-ZmFGK_TLjScIeQRSZEw4dSuIRYIxcla6pbmIHRPqyG3Nde3s7MBkJ"
    secret = "EBTZ5yKSCH2RFpUaZOus7UoUfjf-eGl3dK14axRFcxi_cKdscVP2cBPERWfg2m3fKQBpvJZO0t1C9UH6"
    secret = "EKf2N4fyI48J5ZQKdYFeRG02rVvyOw58m2qzORMg8p7CasKV-TMisE-wiPRCHxkmXCrmUAb8PRPQP1-l"
    auth = basic_authorization(clientid,secret).replace('\n','')

    req = urllib2.Request("https://api.paypal.com/v1/oauth2/token",
    headers = {
       "Accept": "application/json",
       "Accept-Language": "en_US",
       "Authorization": auth
    },data = 'grant_type=client_credentials')
    f = urllib2.urlopen(req)
    token = json.loads(f.read())['access_token']
    request.session['papaltoken'] = token
    return token

def getinvoice(request,invoice):
  token = getToken(request)
  conn = httplib.HTTPSConnection("api.paypal.com")
  conn.request("GET","/v1/invoicing/invoices/"+invoice,
    '',
    {"content-type": "application/json",
     "Accept": "application/json",
     "authorization": "Bearer "+token,
    })
  resp = conn.getresponse()
  conn.close()
  data = resp.read()
  return data


def invoice(request):
  test = json.dumps(invoice_template)
  return createinvoice(request)

"""
This is an unfinished function which is supposed to catch paypal events.
However it never works.
"""
def paypalpdt(request):
  _identity_toke = "1aVupu9gNufeVWLBqkNa619TjsYXgC-ZQd5rUOW_sWiVHR9A8F6zKuTOBFO"
  _identity_toke = "VbcoPtKY7npptth9GdQPW69fbH7DRoK1BBsTNIJDT2waJM_wU4BqGetpxZe"
  if not 'tx' in request.GET:
    return retailError(request,"No Paypal token provided")
  trans_id = request.GET['tx']

  # Confgure POST args
  args = {}
  # Specify the paypal command
  args['cmd'] ='_notify-synch'
  args['tx'] = trans_id
  args['at'] = _identity_token

  args = urllib.urlencode(args) 
  status = ""
  try:
      # Do a post back to validate
      # the transaction data
      status = urlfetch.fetch(url = _paypal_url,
                              method = urlfetch.POST,
                              payload = args).content
  except:
      return retailError(request,"Unknow error, your request might have been processed already")

  a = 1/0
  if re.search('^SUCCESS', status):
      # Check other transaction details here like
      # payment_status etc..
      # Update order status
      return retailError(request,"Unknow error, your request might have been processed already")
  else:
      return retailError(request,"Unknow error, your request might have been processed already")




