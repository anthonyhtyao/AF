from django.shortcuts import render
from auroreformosa.models import *
from auroreformosa.forms import *
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
import urllib
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

def init(request):
    # Set default language to fr
    if not('language' in request.session):
        request.session['language'] = 'fr'
    language = request.session['language']
    returnForm={}
    # Put categories list in return form
    edito = Category.objects.get(category="edito")
    categories = CategoryDetail.objects.filter(language=language).exclude(category = edito)
    returnForm['categories'] = categories
    returnForm['language'] = language
    return returnForm, language

def index(request):
    returnForm, language = init(request)
    comic = Category.objects.get(category="comics")
    comicArticleP = Article.objects.filter(category=comic).order_by('-date')[0]
    comicArticle = comicArticleP.comic.get(language=language)
    returnForm['comicArticle'] = comicArticle
    numeros = Numero.objects.order_by('numero')
    returnForm['numeros'] = numeros
    return render(request, 'AF/index.html', returnForm)

def about(request):
    returnForm, language = init(request)
    return render(request, 'AF/about.html', returnForm)

def uploadImg(request):
    if request.method == 'POST':
        form = ImgForm(request.POST, request.FILES)
        if form.is_valid():
            title = str(request.FILES['imgfile']).split("/")[-1]
            newImg = Img(imgfile = request.FILES['imgfile'],title=title)
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
    elif category == "edito":
        return HttpResponseRedirect("/") 
    else:
        returnForm, language = init(request)
        try:
            cat = Category.objects.get(category=category)
            category = cat.detail.get(language=language)
            articles = []
            for a in Article.objects.filter(category=cat):
                try:
                    articles.append(a.article.get(language=language))
                except:
                    pass
            returnForm['category'] = category
            returnForm['articles'] = articles
            return render(request, 'AF/category.html', returnForm)
        except:
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
    try:
        articleParent = Article.objects.get(slg=slg)
        try:
            cat = Category.objects.get(category = category)
        except:
            cat = None
        if articleParent.category == cat:
            returnForm, language = init(request) 
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
            returnForm['category'] = category
            returnForm['article'] = article
            returnForm['articleRelated'] = articleRelated
            return render(request, 'AF/article.html', returnForm)
        else:
            return HttpResponseRedirect('/'+str(article.category)+'/article/'+slg)
    except:
            return HttpResponseRedirect('/')

def comics(request, slg):
    try:
        returnForm, language = init(request)
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
        returnForm['category'] = category
        returnForm['comic'] = comic
        returnForm['nextComic'] = nextComic
        returnForm['beforeComic'] = beforeComic
        return render(request, 'AF/comics.html', returnForm)
    except:
        return HttpResponseRedirect('/')    

def archive(request, numero):
    try:
        returnForm, language = init(request)
        no = Numero.objects.get(numero=int(numero))
        comicCat = Category.objects.get(category="comics")
        editoP = no.article.get(edito=True)
        edito = editoP.article.get(language=language)
        articles = []
        for a in  no.article.filter(edito = False):
            if a.category == comicCat:
                comic = a.comic.get(language=language)
            else:
                articles.append(a.article.get(language=language))
        returnForm['numero'] = no
        returnForm['articles'] = articles
        returnForm['edito'] = edito
        returnForm['comic'] = comic
        return render(request, 'AF/archiveArticle.html', returnForm)
    except:
        return HttpResponseRedirect('/')

def abonnement(request):
    if request.method=="POST":
        form = AbonnementForm(request.POST)
        if form.is_valid():
            print(request.POST)
            emailTxt = get_template('email.txt')
            emailHtml = get_template('email.html')
            adresse = request.POST['adresse'] + " " + request.POST['city'] + " " + request.POST['country'] + " " + request.POST['codepostal']
            action =""
            try:
                if request.POST['abonnement']:
                    action += "s'abonner , "
            except:
                pass
            try:
                if request.POST['don']:
                    action += "faire un don de "
                    try:
                        action += request.POST['amount']
                    except:
                        action += "0"
                    action += " € , "
            except:
                pass
            try:            
                if request.POST['informer']:
                    action += "être informé(e)"
            except:
                pass
            d = Context({'title':request.POST['title'], 'name':request.POST['name'], 'email':request.POST['email'], 'adresse':adresse, 'action':action, 'message':request.POST['message']})
            textContent = emailTxt.render(d)
            htmlContent = emailHtml.render(d)
            msg = EmailMultiAlternatives("New Subscription", textContent, 'anthonyhtyao@gmail.com', ['anthonyhtyao@gmail.com', 'yulinhuang23@gmail.com', 'jhihhuang.li@gmail.com', 'sun.yujung@gmail.com', 'turtlelin1210@gmail.com'])
            msg.attach_alternative(htmlContent, "text/html")
            msg.send()
    form = AbonnementForm()
    return render(request,'AF/abonnement.html',{'form':form})

def contact(request):
    returnForm, language = init(request)
    return render(request, 'AF/contact.html', returnForm)
