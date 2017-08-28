import django.core.handlers.wsgi
from core import userapi, dbtype 
from django.core.context_processors import csrf
from google.appengine.ext import db,blobstore,deferred

class AdminAction(db.Model):
  date = db.DateProperty(auto_now_add = True)
  action = db.StringProperty(required = True)
  target = db.StringProperty(required = True)


