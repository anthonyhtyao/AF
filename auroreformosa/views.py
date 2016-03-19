from django.shortcuts import render
from auroreformosa.models import *
from auroreformosa.forms import *
from django.http import HttpResponseRedirect, HttpResponse
def sessionLanguage(request):
    if not('language' in request.session):
        request.session['language'] = 'fr'
    return request.session['language']

def index(request):
    sessionLanguage(request)
    return_form={}
    add_categories(request, return_form)
    comic = Category.objects.get(category="comics")
    comicArticleP = Article.objects.filter(category=comic).order_by('-date')[0]
    comicArticle = comicArticleP.comic.get(language=request.session['language'])
    return_form['comicArticle'] = comicArticle
    numeros = Numero.objects.order_by('numero')
    return_form['numeros'] = numeros
    return render(request, 'AF/index.html', return_form)

def about(request):
    sessionLanguage(request)
    return_form={}
    add_categories(request, return_form)
    return render(request, 'AF/about.html', return_form)

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
    if category == "comics":
        comicCat = Category.objects.get(category=category)
        comic = comicCat.article.order_by('-date')[0]
        return HttpResponseRedirect('/comics/' + comic.slg) 
    else:
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
    edito = Category.objects.get(category="edito")
    categories = CategoryDetail.objects.filter(language=request.session['language']).exclude(category = edito)
    return_form['categories'] = categories

def article(request, category, slg):
    language = sessionLanguage(request) 
    try:
        articleParent = Article.objects.get(slg=slg)
        try:
            cat = Category.objects.get(category = category)
        except:
            cat = None
        if articleParent.category == cat:
            category = CategoryDetail.objects.get(language=language, category=cat)
            try:
                article = articleParent.article.get(language=language)
            except:
                article = None
            i = 1
            articleRelated = []
            for a in Article.objects.filter(category=cat).order_by('-date'):
                if i > 4:
                    break
                articleGet = a.article.get(language = language)
                if article != articleGet:
                    articleRelated.append(articleGet)
                    i += 1
            return render(request, 'AF/article.html', {'category':category, 'article':article, 'articleRelated':articleRelated })
        else:
            return HttpResponseRedirect('/'+str(article.category)+'/article/'+slg)
    except:
            return HttpResponseRedirect('/')

def comics(request, slg):
    language = sessionLanguage(request) 
    try:
        articleParent = Article.objects.get(slg=slg)
        cat = Category.objects.get(category="comics")
        category = CategoryDetail.objects.get(language=language, category=cat)
        comics = cat.article.order_by('-date')
        try:
            comic = articleParent.comic.get(language=language)
            l = len(comics)
            for i in range(l):
                if comics[i] == articleParent:
                    break
            if i == 0:
                beforeComic = comics[l-1]
            else:
                beforeComic = comics[i-1]
            if i == l-1:
                nextComic = comics[0]
            else:
                nextComic = comics[i+1]  
        except:
            comic = None
            return HttpResponseRedirect("/")
        return render(request, 'AF/comics.html', {'category':category, 'comic':comic, 'nextComic':nextComic, 'beforeComic':beforeComic})
    except:
        return HttpResponseRedirect('/')    

def archive(request, numero):
    try:
        no = Numero.objects.get(numero=int(numero))
        comicCat = Category.objects.get(category="comics")
        editoP = no.article.get(edito=True)
        edito = editoP.article.get(language=request.session['language'])
        articles = []
        for a in  no.article.filter(edito = False):
            if a.category == comicCat:
                comic = a.comic.get(language=request.session['language'])
            else:
                articles.append(a.article.get(language=request.session['language']))
        return render(request, 'AF/archiveArticle.html', {'numero':no, 'articles':articles, "edito":edito, "comic":comic})
    except:
        return HttpResponseRedirect('/')
