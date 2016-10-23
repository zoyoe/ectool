from django import forms

class form_createworkspace(forms.Form):
  name = forms.CharField(max_length = 20)
  email = forms.EmailField()
  password = forms.CharField(max_length = 20)
