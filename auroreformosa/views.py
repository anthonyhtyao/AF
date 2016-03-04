from django.shortcuts import render
from auroreformosa.forms import *
from auroreformosa.views import *

def index(request):
    return render(request, 'AF/index.html')

def createarticle(request):
    articleForm = ArticleForm()
    numeros = Numero.objects.all()
    return render(request, 'AF/createArticle.html', {'form':articleForm, 'numeros':numeros})
