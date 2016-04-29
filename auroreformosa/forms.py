from django import forms
from auroreformosa.models import *
from tinymce.widgets import TinyMCE

class ImgForm(forms.Form):
    imgfile = forms.FileField(
        label = 'Select a file',
        help_text = 'max. 42 mb'
    )

class ArticleForm(forms.ModelForm):
    title = forms.CharField(max_length = 128)
    content = forms.CharField(widget = TinyMCE(attrs={'cols': 80, 'rows': 3}))

    class Meta:
        model = ArticleContent
        fields = ('language','title','abstract', 'content',)

class ComicForm(forms.Form):
    titleFR = forms.CharField(max_length=128)
    titleTW = forms.CharField(max_length=128, required = False)
    contentFR = forms.CharField(widget = TinyMCE(attrs={'cols': 80, 'rows': 3}), required=False)
    contentTW = forms.CharField(widget = TinyMCE(attrs={'cols': 80, 'rows': 3}), required=False)

class AbonnementForm(forms.Form):
    name = forms.CharField(max_length = 64)
    email = forms.EmailField(max_length = 128)
