from django.shortcuts import render
from auroreformosa.models import *
from auroreformosa.forms import *
from django.http import HttpResponseRedirect, HttpResponse

def index(request):
    if not('language' in request.session):
        request.session['language'] = 'fr'
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

def createarticle(request):
    articleForm = ArticleForm()
    numeros = Numero.objects.all()
    categoryFR = CategoryDetail.objects.filter(language='fr')
    categoryTW = CategoryDetail.objects.filter(language='tw')
    return render(request, 'AF/createArticle.html', {'form':articleForm, 'numeros':numeros, 'categoryFR':categoryFR, 'categoryTW':categoryTW})

def category(request, category):
    categoryList = Category.objects.all()
    inList = False
    for c in categoryList:
        if str(c) == category:
            inList = True
            cat = c
    if inList:
        categoryFR = CategoryDetail.objects.get(language='fr', category=cat)
        categoryTW = CategoryDetail.objects.get(language='tw', category=cat)
        articleFR = [ a for a in ArticleContent.objects.all() if a.language=='fr' and  a.inCategory(cat)]
        articleTW = [ a for a in ArticleContent.objects.all() if a.language=='tw' and  a.inCategory(cat)]
        return render(request, 'AF/category.html', {'categoryFR':categoryFR, 'categoryTW':categoryTW, 'articleFR':articleFR, 'articleTW':articleTW})
    else:
        return HttpResponseRedirect('/')

def session_language(request):
    if request.method == 'POST':
        request.session['language'] = request.POST['language']
        return HttpResponse('123')
