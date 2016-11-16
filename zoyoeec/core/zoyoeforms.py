from django import forms

class CreateWorkspace(forms.Form):
  name = forms.CharField(max_length = 20)
  email = forms.EmailField()
  password = forms.CharField(max_length = 20)
