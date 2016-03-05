from django.shortcuts import render
from auroreformosa.models import *
from auroreformosa.forms import *
from django.http import HttpResponseRedirect, HttpResponse

def index(request):
    if not('language' in request.session):
        request.session['language'] = 'fr'
    return_form={}
    add_categories(request, return_form)
    return render(request, 'AF/index.html', return_form)

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
    categories = CategoryDetail.objects.filter(language=request.session['language'])
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
        return render(request, 'AF/category.html', {'categoryFR':categoryFR, 'categoryTW':categoryTW, 'articleFR':articleFR, 'articleTW':articleTW, 'categories':categories})
    else:
        return HttpResponseRedirect('/')

def session_language(request):
    if request.method == 'POST':
        request.session['language'] = request.POST['language']
        return HttpResponse('123')

def add_categories(request, return_form):
    #Add categories in return_form for the category navbar for each view
    categories = CategoryDetail.objects.filter(language=request.session['language'])
    return_form['categories'] = categories

def article(request, category, slg):
    try:
        article = Article.objects.get(slg=slg)
        try:
            cat = Category.objects.get(category = category)
        except:
            cat = None
        if article.category == cat:
            categoryFR = CategoryDetail.objects.get(language='fr', category=cat)
            categoryTW = CategoryDetail.objects.get(language='tw', category=cat)
            articleFR = ArticleContent.objects.get(language='fr', article = article)
            try:
                articleTW = ArticleContent.objects.get(language='tw', article = article)
            except:
                articleTW = None
            return render(request, 'AF/article.html', {'categoryFR':categoryFR, 'categoryTW':categoryTW, 'articleFR':articleFR, 'articleTW':articleTW})
        else:
            return HttpResponseRedirect('/'+str(article.category)+'/article/'+slg)
    except:
            return HttpResponseRedirect('/')
