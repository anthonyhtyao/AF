from django import forms

class ImgForm(forms.Form):
    imgfile = forms.FileField(
        label = 'Select a file',
        help_text = 'max. 42 mb'
    )
