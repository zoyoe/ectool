from django import forms

class CreateWorkspace(forms.Form):
  name = forms.CharField(max_length = 20)
  email = forms.EmailField()
  password = forms.CharField(max_length = 20)

class AlterConfig(forms.Form):
  title = forms.CharField(max_length = 20)
  type = forms.CharField(max_length = 20)
  content = forms.CharField(max_length = 1024)
  

def fetchError(rf):
  return [(k, rf.error_class.as_text(v)) for k, v in rf.errors.items()]
