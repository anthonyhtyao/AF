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
from auroreformosa.views import *

@login_required
def uploadImg(request):
    returnForm, language = init(request)
    if request.method == 'POST':
        form = ImgForm(request.POST, request.FILES)
        if form.is_valid():
            title = str(request.FILES['imgfile']).split("/")[-1]
            newImg = Img(imgfile = request.FILES['imgfile'],title=title)
            newImg.save()
    else:
        form = ImgForm()
    returnForm['form'] = form
    return render(request,'admin/upload.html', returnForm)

@login_required
def createComic(request, errMsg="", success="", warnMsg=""):
    returnForm, language = init(request)
    if request.method == 'POST':
        form = ComicForm(request.POST)
        if form.is_valid():
            print(request.FILES)
            data = request.POST
            author = UserProfile.objects.get(id=data['author'])
            comicCat = Category.objects.get(category="comics")
            numero = Numero.objects.get(id=data['numero'])
            titleFR = data['titleFR']
            try:
                article = Article.objects.create(title=titleFR)
            except:
                request.method = ""
                return createComic(request, errMsg = "Title already be used")
            article.author = author
            article.category = comicCat
            article.numero = numero
            article.save()
            try:
                imgTitleFR = str(request.FILES['imgfileFR']).split("/")[-1]
                imgFR = Img(imgfile = request.FILES['imgfileFR'],title=imgTitleFR)
                imgFR.save()
                comic = Comic.objects.create(title = titleFR)
                comic.article = article
                comic.image = imgFR
                comic.content = data['contentFR']
                comic.save()
            except:
                request.method = ""
                return createComic(request, errMsg = "ImageFR error")
            titleTW = data['titleTW']
            if titleTW != "":
                try:
                    imgTitleTW = str(request.FILES['imgfileTW']).split("/")[-1]
                    imgTW = Img(imgfile = request.FILES['imgfileTW'],title=imgTitleTW)
                    imgTW.save()
                    comic = Comic.objects.create(title = titleTW)
                    comic.article = article
                    comic.image = imgTW
                    comic.content = data['contentTW']
                    comic.language = "tw"
                    comic.save()
                    request.method = ""
                    return createComic(request, success="Commics FR and TW added successfully. <a class='FR' href=/comics/"+article.slg+"> Click to read Comic FR </a> and <a class='TW' href=/comics/"+article.slg+"> Click to read Comic TW </a>")
                except:
                    pass
            request.method = ""
            return createComic(request, warnMsg = "Comic FR added successfully and Comic TW fail. <a class='FR' href=/comics/"+article.slg+"> Click to read Comic FR </a>")
    comicForm = ComicForm()
    users = UserProfile.objects.all()
    returnForm['form'] = comicForm
    returnForm['users'] = users
    returnForm['errMsg'] = errMsg
    returnForm['warnMsg'] = warnMsg
    returnForm['success'] = success
    return render(request, 'admin/createComic.html', returnForm)

@login_required
def createarticle(request, errMsg=""):
    returnForm, language = init(request)
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            try:
                data = request.POST
                print(data)
                # Create Article
                if (int(data['article']) == 0):
                    numero = Numero.objects.get(id=data['numero'])
                    # Verify edito and headline are unique
                    try:
                        if (data['isEdito']):
                            edito = True
                            if numero.article.filter(edito=True).exists():
                                request.method = ""
                                return createarticle(request, "Edito already exists")
                    except:
                        edito = False
                    try:
                        if (data['isHeadline']):
                            headline = True
                            if numero.article.filter(headline=True).exists():
                                request.method=""
                                return createarticle(request, "Headline already exists")
                    except:
                        headline = False
                    # Create article if title is unique else return
                    try:
                        article = Article.objects.create(title=data['title'])
                    except:
                        request.method = ""
                        return createarticle(request, "Title already be used")

                    # Upload Image
                    try:
                        imgTitle = str(request.FILES['imgfile']).split("/")[-1]
                        img = Img(imgfile = request.FILES['imgfile'],title=imgTitle)
                        img.save()
                        article.image = img
                    except:
                        pass
                    author = UserProfile.objects.get(id=data['author'])
                    if data['language'] == 'fr':
                        category = Category.objects.get(id=data['categoryFR'])
                    else:
                        category = Category.objects.get(id=data['categoryTW'])
                    article.numero = numero
                    article.author = author
                    article.category = category
                    article.edito = edito
                    article.headline = headline
                    article.save()
                # Article already existes
                else:
                    article = Article.objects.get(id=data['article'])
                    category = article.category
                # Create Article Content
                if article.article.filter(language=data['language']):
                    request.method=""
                    return createarticle(request, "Article " + data['language'] + " already exists")
                articleContent = form.save()
                articleContent.article = article
                articleContent.save()
                #Return article created page
                request.session['language'] = data['language']
                return HttpResponseRedirect('/' + str(category) + '/article/' + article.slg)
            except:
                pass
    articleForm = ArticleForm()
    articles = Article.objects.all()
    numeros = Numero.objects.all()
    categoryFR = CategoryDetail.objects.filter(language='fr')
    categoryTW = CategoryDetail.objects.filter(language='tw')
    users = UserProfile.objects.all()
    returnForm['form'] = articleForm
    returnForm['categoryFR'] = categoryFR
    returnForm['categoryTW'] = categoryTW
    returnForm['users'] = users
    returnForm['articles'] = articles
    returnForm['errMsg'] = errMsg
    return render(request, 'admin/createArticle.html', returnForm)

@login_required
def archiveEdit(request):
    returnForm, language = init(request)
    returnForm["data"] = []
    comicCat = Category.objects.get(category="comics")
    for no in returnForm['numeros'][::-1]:
        dist = {'numero' : no}
        # Test if image exists
        image = no.image
        dist["image"] = image
        # Test if edito exists
        try:
            editoP = no.article.get(edito=True)
            try:
                editoFR = editoP.article.get(language="fr")
                dist["editoFR"] = editoFR
            except:
                dist["editoFR"] = ""
            try:
                editoTW = editoP.article.get(language="tw")
                dist["editoTW"] = editoTW
            except:
                dist["editoTW"] = ""
        except:
            dist["editoFR"] = ""
            dist["editoTW"] = ""
        # Test if headline exists
        try:
            headline = no.article.get(headline=True)
            dist["headline"] = headline
        except:
            dist["headline"] = ""
        # Test if comic exists
        try:
            comicP = no.article.filter(category=comicCat)
            comicList = []
            for a in comicP:
                d = {}
                try:
                    comicFR = a.comic.get(language="fr")
                    d["comicFR"] = comicFR
                except:
                    d["comicFR"] = ""
                try:
                    comicTW = a.comic.get(language="tw")
                    d["comicTW"] = comicTW
                except:
                    d["comicTW"] = ""
                comicList.append(d)
            dist["comics"] = comicList
        except:
            dist["comics"] = ""
        articles = []
        for a in  no.article.filter(edito = False).exclude(category = comicCat):
            tmp = {"article":a}
            try:
                tmp["articleFR"] = a.article.get(language="fr")
            except:
                tmp["articleFR"] = ""
            try:
                tmp["articleTW"] = a.article.get(language="tw")
            except:
                tmp["articleTW"] = ""
            articles.append(tmp)
        dist["articles"] = articles
        returnForm["data"].append(dist)
    return render(request, 'admin/archiveEdit.html', returnForm)

@login_required
def createUser(request, msg=""):
    returnForm,language = init(request)
    if request.POST:
        username = request.POST['username']
        email = request.POST['email']
        # Init password 0000
        u = User.objects.create_user(username, email, "0000")
        up = UserProfile()
        up.user = u
        up.name = request.POST['name']
        up.save()
        request.method=""
        msg = "User " + str(up) + " successfully created"
    returnForm["msg"] = msg
    return render(request, 'admin/createUser.html', returnForm)
