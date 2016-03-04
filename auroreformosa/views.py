from django.shortcuts import render
from auroreformosa.forms import *
from auroreformosa.views import *

def index(request):
    return render(request, 'AF/index.html')

def createarticle(request):
    articleForm = ArticleForm()
    numeros = Numero.objects.all()
    categoryFR = CategoryDetail.objects.filter(language='fr')
    categoryTW = CategoryDetail.objects.filter(language='tw')
    return render(request, 'AF/createArticle.html', {'form':articleForm, 'numeros':numeros, 'categoryFR':categoryFR, 'categoryTW':categoryTW})
