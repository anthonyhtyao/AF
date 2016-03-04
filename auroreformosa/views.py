from django.shortcuts import render
from auroreformosa.forms import *

# Create your views here.

def index(request):
    return render(request, 'AF/index.html')

def createarticle(request):
    articleForm = ArticleForm()
    return render(request, 'AF/createArticle.html', {'form':articleForm})
