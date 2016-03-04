from django.shortcuts import render
from auroreformosa.models import *
from auroreformosa.forms import *
from django.http import HttpResponseRedirect

def index(request):
	return render(request, 'AF/index.html')

def uploadImg(request):
    if request.method == 'POST':
        form = ImgForm(request.POST, request.FILES)
        if form.is_valid():
            newImg = Img(imgfile = request.FILES['imgfile'])
            newImg.save()
    else:
        form = ImgForm()
    return render(request,'AF/upload.html',{'form':form})
