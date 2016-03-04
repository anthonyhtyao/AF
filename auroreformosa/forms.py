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
