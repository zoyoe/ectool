import django.core.handlers.wsgi
from django.core.context_processors import csrf
from django.template import loader,Context,RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
import userapi,dbtype,error
import random
import urllib2,httplib
import requests,json,datetime
from google.appengine.ext import db
from google.appengine.api import urlfetch
import re,string

class SupplierOrder(db.Model):
  oid = db.StringProperty(required=True)
  supplier = db.StringProperty(required=True)
  date = db.DateProperty()
  status = db.StringProperty(required=True)

class SupplierItem(db.Model):
  iid = db.StringProperty(required=True)
  rid = db.StringProperty(default="")
  description = db.StringProperty(required=True)
  price = db.FloatProperty()
  cost = db.FloatProperty()
  amount = db.IntegerProperty()

@userapi.authority_item
def saveorder(request):
  order = SupplierOrder(oid = request.POST['supplier_id']
    ,supplier = request.POST['supplier_name']
    ,status = request.POST['order_status']
    ,date = datetime.datetime.now().date())
  order.put()
  if 'details' in request.POST:
    data = json.loads(request.POST['details'])
    while(data):
      row  = data.pop(0)
      siid = row.pop(0)
      name = row.pop(0)
      quantity = int(float(row.pop(0)))
      value = re.search("\d+.\d+", row.pop(0))
      value = float(value.group(0))
      a = SupplierItem(iid = siid,description = name
        ,price = value * 2.2,cost = value,amount = quantity,parent=order)
      a.put()
  return HttpResponseRedirect('/order/orderview/?key='+str(order.key().id()))

@userapi.authority_item
def modifyorder(request):
  k = request.POST['key']
  order = SupplierOrder.get_by_id(int(k))
  order.oid = request.POST['supplier_id']
  order.supplier = request.POST['supplier_name']
  order.status = request.POST['order_status']
  order.date = datetime.datetime.now().date()
  order.put()
  return HttpResponseRedirect('/order/orderview/?key='+str(order.key().id()))

@userapi.authority_item
def deleteorder(request):
  k = request.GET['key']
  order = SupplierOrder.get_by_id(int(k))
  items = SupplierItem.all().ancestor(order)
  for item in items:
    item.delete()
  order.delete()
  return HttpResponseRedirect('/orders/')

@userapi.authority_item
def orderview(request):
  key = request.GET['key']
  order = SupplierOrder.get_by_id(int(key))
  if not order:
    return error.retailError(request,"Order not exist.")
  orderitems = SupplierItem.all().ancestor(order)
  context = Context({'ORDER':order,'ITEMS':orderitems})
  return (render_to_response("order/orderview.html",context,context_instance=RequestContext(request)))

@userapi.authority_item
def deploy(request):
  key = request.GET['key']
  order = SupplierOrder.get_by_id(int(key))
  if not order:
    return error.retailError(request,"Order not exist.")
  orderitems = SupplierItem.all().ancestor(order)
  supplier = dbtype.Supplier.getSupplierByName(order.supplier)
  if not supplier:
    supdata = {'store':order.supplier,
        'category':{'other':{'name':'misc','children':{}}}}
    supplier = dbtype.Supplier(name = order.supplier,data=json.dumps(supdata['category']))
    supplier.put()
  for item in orderitems:
    deployitem(item,supplier)
  return HttpResponseRedirect('/admin/items/'+supplier.name+"/other/")

def deployitem(item,supplier):
  item.rid = item.iid
  iteminfo = {
    'refid':item.rid,
    'name':item.description,
    'price':item.price,
    'cost':item.cost,
    'galleryurl':'http://zoyoeimage.appspot.com/images/'+supplier.name+'/'+item.iid+'_crop.jpg',
    'infourl':'/item/'+item.rid+"/",
    'category':'other',
    'sndcategory':'other',
    'ebayid': None,
    'specification':'{}',
    'description':'No extra description provided'
  }
  item.put()
  supplier.saveItem(iteminfo,False)

### A view that returns all the recepits 
###
@userapi.authority_item
def orders(request):
  receipts = db.GqlQuery("SELECT * FROM SupplierOrder ORDER BY date DESC")
  context = Context({'ORDERS':receipts,'ebayinfo':getEbayInfo(request)})
  return (render_to_response("order/orders.html",context,context_instance=RequestContext(request)))


