import webapp2,json
from django import template
from django.utils.html import escape
from google.appengine.api import users
from core import dbtype as site
register = template.Library()
import core.userapi

@register.filter("shopinfo")
def shopinfo(infotype, *args, **kwargs):
  return site.ShopInfo.all().filter("type =",str(infotype)).order("name")

@register.filter("templatethingy")
def templatethingy(tname, *args, **kwargs):
  return site.getSiteInfo().getTemplate(tname + ".thingy")

@register.filter("templatejs")
def templatejs(tname, *args, **kwargs):
  return site.getSiteInfo().getTemplate(tname + ".js")

