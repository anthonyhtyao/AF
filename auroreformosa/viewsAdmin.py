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
from django.forms.models import formset_factory
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.urlresolvers import reverse

@login_required
def uploadImg(request):
    returnForm, language = init(request)
    ImageFormSet = formset_factory(form=ImgForm, extra = 3, max_num=10)
    if request.method == 'POST':
        formset = ImageFormSet(request.POST, request.FILES)
        if formset.is_valid():
            for form in formset.cleaned_data:
                if form != {}:
                    title = str(form['imgfile'])
                    newImg = Img(imgfile = form['imgfile'], title=title)
                    newImg.save()
    returnForm['formset'] = ImageFormSet
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
    # Get variable details by geet request
    try:
        no = request.GET['no']
    except:
        no = 1
    returnForm['currentNumero'] = float(no)
    returnForm['form'] = comicForm
    returnForm['users'] = users
    returnForm['errMsg'] = errMsg
    returnForm['warnMsg'] = warnMsg
    returnForm['success'] = success
    return render(request, 'admin/createComic.html', returnForm)

# Set article's status to 1 (article editting) and go to preview page if success
@login_required
def createarticle(request, errMsg="", msg=""):
    returnForm, language = init(request)
    # Gallery is a imgform set
    ImageFormSet = formset_factory(form=ImgForm, extra = 3, max_num=10)
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
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

                    # Upload gallery
                    for f in formset.cleaned_data:
                        if f != {}:
                            title = str(f['imgfile'])
                            newImg = Img(imgfile = f['imgfile'], title=title)
                            newImg.save()
                            article.gallery.add(newImg)

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
                    article.timeline = TimelineEvent.objects.get(id=data['timeline'])
                    article.save()
                # Article already existes and set its status to 1
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
                article.status = 1
                article.save()
                #Return article preview page
                request.session['language'] = data['language']
                return HttpResponseRedirect(reverse('articlePreview', args=(str(article.category),article.slg,)))
            except:
                pass
    articleForm = ArticleForm()
    articles = Article.objects.all()
    numeros = Numero.objects.all()
    categoryFR = CategoryDetail.objects.filter(language='fr')
    categoryTW = CategoryDetail.objects.filter(language='tw')
    users = UserProfile.objects.all()
    # Get no version details by get request
    try:
        no = request.GET['no']
    except:
        no = 1
    returnForm['formset'] = ImageFormSet
    returnForm['currentNumero'] = float(no)
    returnForm['form'] = articleForm
    returnForm['categoryFR'] = categoryFR
    returnForm['categoryTW'] = categoryTW
    returnForm['users'] = users
    returnForm['articles'] = articles
    returnForm['errMsg'] = errMsg
    returnForm['msg'] = msg
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
        for a in  no.article.filter(edito = False).exclude(status = 0).exclude(category = comicCat):
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

@login_required
def articleEdit(request, category, slg, errMsg="", msg=""):
    returnForm, language = init(request)
    currentArticle = Article.objects.get(slg=slg)
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        data = request.POST
        articleContent = currentArticle.article.get(language=language)
        articleContent.title = data['title']
        articleContent.abstract = data['abstract']
        articleContent.content = data['content']
        articleContent.save()
        currentArticle.status = 1
        currentArticle.save()
        return HttpResponseRedirect(reverse('articlePreview', args=(str(category),slg,)))
    else:
        try:
            currentArticleContent = currentArticle.article.get(language=language)
        except:
            return HttpResponseRedirect('/')
        returnForm['currentArticle'] = currentArticle
        returnForm['currentArticleContent'] = currentArticleContent
        returnForm['currentCategory'] = currentArticle.category
        returnForm['currentNumero'] = currentArticle.numero
        returnForm['currentGallery'] = currentArticle.gallery.all()
        msg = "Edit article <b>" + str(currentArticleContent) + "</b>. <br/>Can only edit title, abstract and content. <a href=/"+str(currentArticle.category)+"/article/"+currentArticle.slg+"/editinfo>Click here</a> to modify artilcle's information"
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
        returnForm['edito'] = currentArticle.edito
        returnForm['headline'] = currentArticle.headline
        returnForm['timeline'] = currentArticle.timeline.id
        eventDetail = currentArticle.timeline.detail.get(language=language)
        returnForm['timelineDetail'] = currentArticle.timeline.start.strftime('%Y-%m-%d') + " " + eventDetail.content
        returnForm['errMsg'] = errMsg
        returnForm['msg'] = msg
        return render(request, 'admin/createArticle.html', returnForm)

@login_required
def articleEditInfo(request, category, slg, errMsg="", msg=""):
    returnForm, language = init(request)
    ImageFormSet = formset_factory(form=ImgForm, extra = 3, max_num=10)
    try:
        currentArticle = Article.objects.get(slg=slg)
        currentArticleContent = currentArticle.article.get(language=language)
    except:
        return HttpResponseRedirect('/')
    currentGallery = [{'imgfile':x.imgfile} for x in currentArticle.gallery.all()]
    if request.method == 'POST':
        data = request.POST
        numero = Numero.objects.get(id=data['numero'])
        formset = ImageFormSet(request.POST, request.FILES,initial=currentGallery)
        try:
            if (data['isEdito']):
                edito = True
                if numero.article.get(edito=True) != currentArticle:
                    request.method = ""
                    return articleEditInfo(request, category,slg,errMsg="Edito already exists")
        except:
            edito = False
        try:
            if (data['isHeadline']):
                headline = True
                if numero.article.get(headline=True) != currentArticle:
                    request.method=""
                    return articleEditInfo(request, category,slg,errMsg="Headline already exists")
        except:
            headline = False
        try:
            imgTitle = str(request.FILES['imgfile']).split("/")[-1]
            img = Img(imgfile = request.FILES['imgfile'],title=imgTitle)
            img.save()
            currentArticle.image = img
        except:
            pass

        # Clean article gallery
        currentArticle.gallery.clear()
        for f in formset.cleaned_data:
            if f != {}:
                # Create a new class Img if image is new
                if type(f['imgfile']) == InMemoryUploadedFile:
                    title = str(f['imgfile'])
                    newImg = Img(imgfile = f['imgfile'], title=title)
                    newImg.save()
                    currentArticle.gallery.add(newImg)
                else:
                    # Find Img object for a image file given
                    img = Img.objects.get(imgfile=f['imgfile'])
                    currentArticle.gallery.add(img)

        category = Category.objects.get(id=data['category'])
        currentArticle.numero = numero
        currentArticle.category = category
        currentArticle.edito = edito
        currentArticle.headline = headline
        currentArticle.timeline = TimelineEvent.objects.get(id=data['timeline'])
        currentArticle.save()
        request.method = ""
        return articleEdit(request,category,slg)
    else:
        currentFormSet = ImageFormSet(initial=currentGallery)
        returnForm['currentFormSet'] = currentFormSet
        returnForm['currentArticle'] = currentArticle
        returnForm['currentCategory'] = currentArticle.category
        returnForm['currentNumero'] = currentArticle.numero
        msg = "Edit article <b>" + str(currentArticleContent) + "</b>'s information. <a href=/"+str(currentArticle.category)+"/article/"+currentArticle.slg+"/edit> Back to edit article </a>"
        numeros = Numero.objects.all()
        categories = CategoryDetail.objects.filter(language=language)
        users = UserProfile.objects.all()
        returnForm['categories'] = categories
        returnForm['users'] = users
        returnForm['edito'] = currentArticle.edito
        returnForm['headline'] = currentArticle.headline
        returnForm['timeline'] = currentArticle.timeline.id
        eventDetail = currentArticle.timeline.detail.get(language=language)
        returnForm['timelineDetail'] = currentArticle.timeline.start.strftime('%Y-%m-%d') + " " + eventDetail.content
        returnForm['errMsg'] = errMsg
        returnForm['msg'] = msg
        return render(request, 'admin/editArticleInfo.html', returnForm)

@login_required
def settings(request,errMsg="", msg=""):
    returnForm, language = init(request)
    currentUser = UserProfile.objects.get(user=request.user)
    if request.method =='POST':
        data = request.POST
        if not request.user.check_password(data['OldPassword']):
            errMsg="Wrong password"
            request.method=""
            return settings(request,errMsg=errMsg)
        else:
            request.method=""
            if currentUser.name != data['InputName']:
                currentUser.name = data['InputName']
                currentUser.save()
                msg = "User's name is sucessfully changed. "
            if data['InputPassword1'] != "":
                if data['InputPassword1'] != data['InputPassword2']:
                    errMsg = "These two new passwords don't match"
                    return settings(request,errMsg=errMsg, msg=msg)
                else:
                    request.user.set_password(data['InputPassword1'])
                    request.user.save()
                    msg += "Password is successfully changed."
            return settings(request,msg=msg)
    returnForm['currentUser'] = currentUser
    returnForm['errMsg'] = errMsg
    returnForm['msg'] = msg
    return render(request, 'admin/settings.html',returnForm)

@login_required
def articlePreview(request,category,slg):
    if request.method == 'POST':
        a = Article.objects.get(slg=slg)
        a.status = 2
        a.save()
        return HttpResponseRedirect(reverse('article', args=(str(a.category),a.slg,)))
    else:
        return article(request,category,slg,status=1)

@login_required
def timelineEdit(request):
    returnForm, language = init(request)
    return render(request, 'admin/timelineEdit.html',returnForm)

@login_required
def timelineSave(request):
    returnForm, language = init(request)
    if request.method=="POST":
        data = request.POST
        start = data['start']
        end = data['end']
        event = TimelineEvent.objects.create(start=start)
        if end!="":
            event.end = end
        event.save()
        detail_fr = TimelineEventDetail.objects.create(content=data['fr'],language="fr")
        detail_fr.event=event
        detail_fr.save();
        return  HttpResponseRedirect('/timeline/edit')
    return HttpResponseRedirect('/')
