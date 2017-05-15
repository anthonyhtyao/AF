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
from django.conf import settings
from django.contrib.auth.models import User
from abo.models import *
from django.db.models import Max
from utils import sendEmail

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

    returnForm['LANGUAGES'] = settings.LANGUAGES
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
            for a in Article.objects.filter(category=cat).order_by('-date'):
                try:
                    d = {}
                    article = a.article.get(language=language,status=2)
                    d['title'] = article.title
                    d['abstract'] = article.abstract
                    d['slg'] = a.slg
                    d['category'] = a.category
                    d['catTranslate'] = str(a.category.detail.get(language=language))
                    d['image'] = a.image
                    articles.append(d)
                except:
                    pass
            returnForm['category'] = cat
            returnForm['catTranslate'] = str(category)
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

def article(request, category, slg, status=2, selectedLang=None):
    try:
        articleParent = Article.objects.get(slg=slg)
        try:
            cat = Category.objects.get(category = category)
        except:
            cat = None
        if articleParent.category == cat:
            returnForm, language = init(request)
            selectedLang = request.GET.get('lang',selectedLang)
            if not selectedLang:
                selectedLang = language
            category = CategoryDetail.objects.get(language=language, category=cat)
            try:
                article = articleParent.article.get(language=selectedLang)
                assert article.status == status
            except:
                article = None
            i = 1
            articleRelated = []
            try:
                for a in Article.objects.filter(category=cat).order_by('-date'):
                    tmp = {}
                    if i > 4:
                        break
                    articleGet = a.article.get(language = language)
                    if article != articleGet:
                        tmp['title'] = articleGet.title
                        tmp['categoryDetail'] = a.category.detail.get(language=language)
                        tmp['category'] = a.category
                        tmp['image'] = a.image
                        tmp['slg'] = a.slg
                        articleRelated.append(tmp)
                        i += 1
            except:
                pass
            returnForm['selectedLang'] = selectedLang
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
        comics = [c for c in cat.article.order_by('date') if c.languageIsExist(language)]
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
        titles = {'M.':'Ms','Mme':'Mm','Mlle':'Ml'}
        currentNo = int(Numero.objects.all().aggregate(Max('numero'))['numero__max'])
        print("haha")
        if form.is_valid():
            data = request.POST
            print(data)
            familyName = data['familyName']
            name = data['name']
            #adressClient = data['adresse']+'\r'+data['codepostal']+" "+data['city']+" "+data['country']
### Create client object
            #client = Subscriber.objects.create(civilite=titles[data['title']],family_name=familyName,name=name,email=data['email'],adress=adressClient,country=data['country'])
            adresse = data['adresse'] + " " + data['city'] + " " + data['country'] + " " + data['codepostal']
            action =""
            """
            try:
                if data['abonnement']:
                    action += "s'abonner , "
                    Subscription.objects.create(subscriber=client,start=currentNo,end=currentNo+4)
            except:
                pass
            try:
                if data['don']:
                    action += "faire un don de "
                    try:
                        action += data['amount']
                        Donation.objects.create(donor=client,amount=int(data['amount']))
                    except:
                        action += "0"
                    action += " € , "
            except:
                pass
            try:
                if data['informer']:
                    action += "être informé(e)"
                    client.info = True
                    client.save()
            except:
                pass
            """
            d = {'title':data['title'], 'familyName':data['familyName'], 'name':data['name'], 'email':data['email'], 'adresse':adresse, 'action':action, 'message':data['message']}
            r = sendEmail(txt='email.txt',html='email.html',data=d,title='test',to=['anthonyhtyao@gmail.com'])
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

def authorArticle(request, slg):
    returnForm, language = init(request)
    try:
        usrP = UserProfile.objects.get(slg=slg)
        articles = []
        for a in usrP.article_set.all().order_by('-date'):
            print(a)
            try:
                d = {}
                article = a.article.get(language=language,status=2)
                d['title'] = article.title
                d['abstract'] = article.abstract
                d['slg'] = a.slg
                d['category'] = a.category
                d['catTranslate'] = str(a.category.detail.get(language=language))
                d['image'] = a.image
                articles.append(d)
            except:
                pass
        returnForm['catTranslate'] = str(usrP)
        returnForm['articles'] = articles
        return render(request, 'AF/category.html', returnForm)
    except:
        return HttpResponseRedirect('/')

def event(request, slg):
    returnForm, language=init(request)
    timelineEvent = TimelineEvent.objects.get(slg=slg)
    articles = []
    for a in timelineEvent.article_set.all():
            try:
                d = {}
                article = a.article.get(language=language,status=2)
                d['title'] = article.title
                d['abstract'] = article.abstract
                d['slg'] = a.slg
                d['category'] = a.category
                d['catTranslate'] = str(a.category.detail.get(language=language))
                d['image'] = a.image
                articles.append(d)
            except:
                pass
    returnForm['articles'] = articles
    returnForm['event'] = timelineEvent
    returnForm['eventDetail'] = timelineEvent.detail.get(language=language)
    return render(request, 'AF/timeline_event.html',returnForm)

