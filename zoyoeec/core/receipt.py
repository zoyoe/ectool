from retailtype import *
import zuser
from google.appengine.ext import db

class Receipt(db.Model):
  date = db.DateProperty()
  email = db.StringProperty(default='xgao@zoyoe.com')
  firstname = db.StringProperty(default = 'anonymous')
  lastname = db.StringProperty(default='guest')
  business = db.StringProperty(default='not provided')
  address = db.StringProperty(default='{}')
  status = db.StringProperty(default='draft')
  paypal = db.StringProperty(default="")
  zuser = db.ReferenceProperty(zuser.UserInfo)
  total = db.FloatProperty(default=0.0)

class ReceiptItem(db.Model):
  iid = db.StringProperty(required=True)
  description = db.StringProperty(required=True)
  date = db.DateProperty()
  price = db.FloatProperty()
  amount = db.IntegerProperty()

