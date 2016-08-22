from django.shortcuts import render
from auroreformosa.models import *
from auroreformosa.forms import *
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail
import urllib
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import random
from django.core import serializers
import json

def init(request):
    # Set default language to fr
    if not('language' in request.session):
        request.session['language'] = 'fr'
    language = request.session['language']
    returnForm={}
    # Put categories list in return form
    edito = Category.objects.get(category="edito")
    cat = Category.objects.exclude(category=edito).order_by('order')
    categories = [a.detail.get(language=language) for a in cat]
    numeros = Numero.objects.order_by('numero')
    newsCat = Category.objects.get(category="news")
    newsDetail = newsCat.detail.get(language=language)
    newsArticles = []
    for a in Article.objects.filter(category=newsCat):
        try:
            newsArticles.append(a.article.get(language=language))
        except:
            pass

    returnForm['numeros'] = numeros
    returnForm['categories'] = categories
    returnForm['language'] = language
    returnForm['newsDetail'] = newsDetail
    returnForm['newsArticles'] = newsArticles
    return returnForm, language

# Return newest article's rule
def newestArticle(request, comic, language):
    # Exclude edito and comic
    articlesP = Article.objects.exclude(headline=True).exclude(category=comic).exclude(edito=True).order_by('-date')
    # Get article list where article exists for language given

    articles = []
    for a in articlesP:
        try:
            articles.append(a.article.get(language=language,status=2))
        except:
            pass
    l = len(articles)
    print(l)
    if l >= 5:
        randomL = random.sample(range(5),3)
    else:
        randomL = random.sample(range(l),3)
    newestArticle1 = articles[randomL[0]]
    newestArticle1Cat = articles[randomL[0]].article.category.detail.get(language=language)
    newestArticle2 = articles[randomL[1]]
    newestArticle2Cat = articles[randomL[1]].article.category.detail.get(language=language)
    newestArticle3 = articles[randomL[2]]
    newestArticle3Cat = articles[randomL[2]].article.category.detail.get(language=language)
    return newestArticle1, newestArticle1Cat, newestArticle2, newestArticle2Cat, newestArticle3, newestArticle3Cat

def index(request, loginMsg=""):
    returnForm, language = init(request)
    comic = Category.objects.get(category="comics")
    for n in returnForm['numeros'][::-1]:
        if int(n.numero) == n.numero:
            returnForm['headerImage'] = n.image
            break
    newestNumero = returnForm['numeros'][::-1][0]
    # Filter here can be optimised
    comicArticleP = Article.objects.filter(category=comic).order_by("-date")
    comicArticle = [a.comic.get(language=language) for a in comicArticleP if a.languageIsExist(language)][0]
    headlineP = Article.objects.filter(headline=True).order_by("-date")
    headline = [h.article.get(language=language) for h in headlineP if h.languageIsExist(language)][0]
    headlineCat = headline.article.category.detail.get(language=language)
    newestArticle1, newestArticle1Cat, newestArticle2, newestArticle2Cat, newestArticle3, newestArticle3Cat = newestArticle(request, comic, language)

    returnForm['newestArticle1'] = newestArticle1
    returnForm['newestArticle1Cat'] = newestArticle1Cat
    returnForm['newestArticle2'] = newestArticle2
    returnForm['newestArticle2Cat'] = newestArticle2Cat
    returnForm['newestArticle3'] = newestArticle3
    returnForm['newestArticle3Cat'] = newestArticle3Cat
    returnForm['comicArticle'] = comicArticle
    returnForm['loginMsg'] = loginMsg
    returnForm['headline'] = headline
    returnForm['headlineCat'] = headlineCat
    return render(request, 'AF/index.html', returnForm)

def about(request):
    returnForm, language = init(request)
    return render(request, 'AF/about.html', returnForm)

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
                    articles.append(a.article.get(language=language,status=2))
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

def article(request, category, slg, status=2):
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
                assert article.status == status
            except:
                article = None
            i = 1
            articleRelated = []
            try:
                for a in Article.objects.filter(category=cat).order_by('-date'):
                    if i > 4:
                        break
                    articleGet = a.article.get(language = language)
                    if article != articleGet:
                        articleRelated.append(articleGet)
                        i += 1
            except:
                pass
            returnForm['category'] = category
            returnForm['article'] = article
            returnForm['authors'] = article.article.author.all()
            returnForm['gallery'] = article.article.gallery.all()
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
        comics = [c for c in cat.article.order_by('-date') if c.languageIsExist(language)]
        try:
            comic = articleParent.comic.exclude(status=0).get(language=language)
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
        returnForm['authors'] = articleParent.author.all()
        return render(request, 'AF/comics.html', returnForm)
    except:
        return HttpResponseRedirect('/')

def archive(request, numero):
    try:
        returnForm, language = init(request)
        no = Numero.objects.get(numero=float(numero))
        comicCat = Category.objects.get(category="comics")
        editoP = no.article.get(edito=True)
        edito = editoP.article.get(language=language)
        articles = []
        for a in  no.article.filter(edito = False):
            d = {}
            try:
                try:
                    article = a.comic.get(language=language,status=2)
                except:
                    article = a.article.get(language=language,status=2)
                d['slg'] = a.slg
                d['category'] = str(a.category)
                d['title'] = str(article)
                d['catTranslate'] = str(a.category.detail.get(language=language))
                articles.append(d)
            except:
                pass
        print(articles)
        returnForm['numero'] = no
        returnForm['articles'] = articles
        returnForm['edito'] = edito
        return render(request, 'AF/archiveArticle.html', returnForm)
    except:
        return HttpResponseRedirect('/')

def abonnement(request):
    returnForm, language = init(request)
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
    returnForm['form'] = form
    return render(request,'AF/abonnement.html', returnForm)

def contact(request):
    returnForm, language = init(request)
    return render(request, 'AF/contact.html', returnForm)

def userLogin(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return index(request, "Wait for activation")
        else:
            return index(request, "Login Error")
    else:
        return index(request, "Login Error")

@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/')

def timelinedata(request):
    returnForm, language = init(request)
    if request.method == 'GET':
        data = {}
        # data['result'] = []
        events = TimelineEvent.objects.all();
        details = []
        for event in events:
            detail = event.detail.get(language=language)
            details.append(detail)
        data['events'] = serializers.serialize('json', events)
        data['details'] = serializers.serialize('json', details)
        return  HttpResponse(json.dumps(data), content_type="application/json")
    return HttpResponseRedirect('/')
