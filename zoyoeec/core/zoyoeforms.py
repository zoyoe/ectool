from django import forms

class CreateWorkspace(forms.Form):
  name = forms.CharField(max_length = 20)
  email = forms.EmailField()
  password = forms.CharField(max_length = 20)

class Supplier(forms.Form):
  name = forms.CharField(max_length = 40)
  data = forms.CharField(max_length = 2048)
  lock = forms.BooleanField(required = False)
  command = forms.CharField(max_length = 32)

class Config(forms.Form):
  title = forms.CharField(max_length = 50)
  type = forms.CharField(max_length = 20)
  content = forms.CharField(max_length = 1024)
  command = forms.CharField(max_length = 32)

class Item(forms.Form):
  name = forms.CharField(max_length = 50)
  refid = forms.CharField(max_length = 50)
  price = forms.DecimalField(decimal_places = 2)
  cost = forms.DecimalField(decimal_places = 2)
  description = forms.CharField(max_length = 2048)
  specification = forms.CharField(max_length = 1024)
  category = forms.CharField(max_length = 50)
  sndcategory = forms.CharField(max_length = 50)
  ebaycategory = forms.CharField(max_length = 50)
  disabled = forms.BooleanField(required = False)

def fetchError(rf):
  return dict((key, rf.error_class.as_text(value)) for (key, value) in rf.errors.items())

def constructError(key, value):
  return {key:value}
