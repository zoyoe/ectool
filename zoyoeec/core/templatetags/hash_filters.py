import webapp2,json
from django import template
from django.utils.html import escape
from google.appengine.api import users
register = template.Library()
import core.zuser

@register.filter("hash")
def hash(dict,key):
  "Return the value of a key in a dictionary. "
  if(dict and dict.has_key(key)):
    return dict[key]
  else:
    return None

@register.filter("jhash")
def jhash(dstr,key):
  "Return the value of a key in a dictionary. "
  dict = json.loads(dstr)
  if(dict and dict.has_key(key)):
    return dict[key]
  else:
    return None

@register.filter("loginurl")
def loginurl(user,request):
  absoluteurl = request.build_absolute_uri()
  return "/login/?requesturl=" + core.zuser.encrypt("url",absoluteurl)

@register.filter("googleloginurl")
def googleloginurl(user,encurl):
  absoluteurl = core.zuser.decrypt("url",encurl)
  return users.create_login_url(absoluteurl)

@register.filter("logouturl")
def logouturl(user,request):
  if(user.oauth):
    absoluteurl = request.path
    return users.create_logout_url(absoluteurl)
  else:
    return "/logout/"

def do_fullescape(parser,token):
  nodelist = parser.parse('endfullescape')
  parser.delete_first_token()
  return EscapeNode(nodelist)

class EscapeNode(template.Node):
  def __init__(self,nodelist):
    self.nodelist = nodelist
  def render(self,context):
    data_str = self.nodelist.render(context)
    return escape(data_str)

register.tag("fullescape",do_fullescape)

@register.simple_tag()
def multiply(qty, unit_price, *args, **kwargs):
    # you would need to do any localization of the result here
    return qty * unit_price
