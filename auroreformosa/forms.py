from django import forms
from auroreformosa.models import *

class ImgForm(forms.Form):
    imgfile = forms.FileField(
        label = 'Select a file',
        help_text = 'max. 42 mb'
    )

class ArticleForm(forms.ModelForm):
    title = forms.CharField(max_length = 128)
    subtitle = forms.CharField(max_length = 128,required=False)
    content = forms.CharField(widget = forms.Textarea)

    class Meta:
        model = ArticleContent
        fields = ('language','title','subtitle','abstract', 'content',)

class ComicForm(forms.Form):
    titleFR = forms.CharField(max_length=128)
    titleTW = forms.CharField(max_length=128, required = False)
    contentFR = forms.CharField(widget = forms.Textarea, required=False)
    contentTW = forms.CharField(widget = forms.Textarea, required=False)

class AbonnementForm(forms.Form):
    name = forms.CharField(max_length = 64)
    email = forms.EmailField(max_length = 128)
