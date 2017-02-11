from django import forms
from abo.models import *

class ClientForm(forms.ModelForm):
    family_name = forms.CharField(max_length=63)
    name = forms.CharField(max_length=63)
    email = forms.EmailField(max_length=127)
    country = forms.CharField(max_length=63)
    info = forms.BooleanField(required=False)
    civilite = forms.ChoiceField(choices=Subscriber.CIVILITE)
    adress = forms.CharField(widget=forms.Textarea)
    remark = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Subscriber
        fields = ['family_name','name','email','country','info','civilite','adress','remark']
