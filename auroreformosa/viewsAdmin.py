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
                    newImg = Img(imgfile = form['imgfile'], imgfile_m = form['imgfile'], imgfile_s = form['imgfile'], title=title)
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
            comicCat = Category.objects.get(category="comics")
            numero = Numero.objects.get(id=data['numero'])
            titleFR = data['titleFR']
            try:
                article = Article.objects.create(title=titleFR)
            except:
                request.method = ""
                return createComic(request, errMsg = "Title already be used")
            for authorId in data.getlist('author'):
                author = UserProfile.objects.get(id=int(authorId))
                article.author.add(author)
            article.category = comicCat
            article.numero = numero
            article.save()
            try:
                form = request.FILES
                imgTitleFR = str(form['imgfileFR']).split("/")[-1]
                imgFR = Img(imgfile = form['imgfileFR'], imgfile_m = form['imgfileFR'], imgfile_s = form['imgfileFR'], title=imgTitleFR)
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
                    imgTitleTW = str(form['imgfileTW']).split("/")[-1]
                    imgTW = Img(imgfile = form['imgfileTW'], imgfile_m = form['imgfileTW'], imgfile_s = form['imgfileTW'], title=imgTitleTW)
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

@login_required
def comicsEdit(request, slg, errMsg="", success="", warnMsg=""):
    returnForm, language = init(request)
    articleParent = Article.objects.get(slg=slg)
    comicFR = None
    comicTW = None
    try:
        comicFR = articleParent.comic.get(language="fr")
        returnForm['comicFR'] = comicFR
    except:
        pass
    try:
        comicTW = articleParent.comic.get(language="tw")
        returnForm['comicTW'] = comicTW
    except:
        pass
    if request.method == 'POST':
        form = ComicForm(request.POST)
        if form.is_valid():
            print(request.FILES)
            data = request.POST
            numero = Numero.objects.get(id=data['numero'])
            for authorId in data.getlist('author'):
                author = UserProfile.objects.get(id=int(authorId))
                articleParent.author.add(author)
            articleParent.numero = numero
            articleParent.save()
            if comicFR:
                comicFR.title = data['titleFR']
                comicFR.content = data['contentFR']
                comicFR.save()
            else:
                try:
                    form = request.FILES
                    imgTitleFR = str(form['imgfileFR']).split("/")[-1]
                    imgFR = Img(imgfile = form['imgfileFR'], imgfile_m = form['imgfileFR'], imgfile_s = form['imgfileFR'], title=imgTitleFR)
                    imgFR.save()
                    comic = Comic.objects.create(title = data['titleFR'])
                    comic.article = article
                    comic.image = imgFR
                    comic.content = data['contentFR']
                    comic.save()
                    comicFR = comic
                except:
                    request.method = ""
                    return comicsEdit(request, errMsg = "ImageFR error")
                if comicTW:
                    comicTW.title = data['titleTW']
                    comicTW.content = data['contentTW']
                    comictW.save()
                else:
                    try:
                        form = request.FILES
                        imgTitleTW = str(form['imgfileTW']).split("/")[-1]
                        imgTW = Img(imgfile = form['imgfileTW'], imgfile_m = form['imgfileTW'], imgfile_s = form['imgfileTW'], title=imgTitleTW)
                        imgTW.save()
                        comic = Comic.objects.create(title = data['titleTW'])
                        comic.article = article
                        comic.image = imgTW
                        comic.content = data['contentTW']
                        comic.save()
                        comicTW = comic
                    except:
                        request.method = ""
                        return comicsEdit(request, errMsg = "ImageTW error")

    comicForm = ComicForm()
    users = UserProfile.objects.all()
    # Get variable details by geet request
    try:
        no = request.GET['no']
    except:
        no = 1
    returnForm['currentNumero'] = float(no)
    returnForm['authors'] = articleParent.author.all()
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
                        img = Img(imgfile = request.FILES['imgfile'], imgfile_m = request.FILES['imgfile'], imgfile_s = request.FILES['imgfile'], title=imgTitle)
                        img.save()
                        article.image = img
                    except:
                        pass

                    # Upload gallery
                    for f in formset.cleaned_data:
                        if f != {}:
                            title = str(f['imgfile'])
                            newImg = Img(imgfile = f['imgfile'], imgfile_m = f['imgfile'], imgfile_s = f['imgfile'], title=title)
                            newImg.save()
                            article.gallery.add(newImg)
                    for authorId in data.getlist('author'):
                        author = UserProfile.objects.get(id=int(authorId))
                        article.author.add(author)
                    if data['language'] == 'fr':
                        category = Category.objects.get(id=data['categoryFR'])
                    else:
                        category = Category.objects.get(id=data['categoryTW'])
                    article.numero = numero
                    article.category = category
                    article.edito = edito
                    article.headline = headline
                    if data['timeline'] > "0":
                        article.timeline = TimelineEvent.objects.get(id=data['timeline'])
                    else:
                        article.timeline = None
                    article.save()
                # Article already existes and set its content's status to 1
                else:
                    article = Article.objects.get(id=data['article'])
                    category = article.category
                # Create Article Content
                if article.article.filter(language=data['language']):
                    request.method=""
                    return createarticle(request, "Article " + data['language'] + " already exists")
                articleContent = form.save()
                articleContent.article = article
                articleContent.status = 1
                articleContent.save()
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
        for a in  no.article.filter(edito = False).exclude(category = comicCat):
            tmp = {"article":a}
            try:
                tmp["articleFR"] = a.article.exclude(status=0).get(language='fr')
            except:
                tmp["articleFR"] = ""
            try:
                tmp["articleTW"] = a.article.exclude(status=0).get(language='tw')
            except:
                tmp["articleTW"] = ""
            print(tmp)
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
        returnForm['currentAuthors'] = currentArticle.author.all()
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
        try:
            returnForm['timeline'] = currentArticle.timeline.id
            eventDetail = currentArticle.timeline.detail.get(language=language)
            returnForm['timelineDetail'] = currentArticle.timeline.start.strftime('%Y-%m-%d') + " " + eventDetail.content
        except:
            returnForm['timeline'] = 0
            returnForm['timelineDetail'] = "Null"
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
        for authorId in data.getlist('author'):
            author = UserProfile.objects.get(id=int(authorId))
            currentArticle.author.add(author)
        try:
            edito = bool(data['isEdito'])
        except:
            edito = False
        if edito:
            try:
                if numero.article.get(edito=True) != currentArticle:
                    request.method = ""
                    return articleEditInfo(request, category,slg,errMsg="Edito already exists")
            except:
                pass
        try:
            headline = bool(data['isHeadline'])
        except:
            headline = False
        if headline:
            try:
                if numero.article.get(headline=True) != currentArticle:
                    request.method=""
                    return articleEditInfo(request, category,slg,errMsg="Headline already exists")
            except:
                pass
        try:
            f = request.FILES
            imgTitle = str(f['imgfile']).split("/")[-1]
            img = Img(imgfile = f['imgfile'], imgfile_m = f['imgfile'], imgfile_s = f['imgfile'], title=imgTitle)
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
                    newImg = Img(imgfile = f['imgfile'], imgfile_m = f['imgfile'], imgfile_s = f['imgfile'], title=title)
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
        if data['timeline'] > "0":
            currentArticle.timeline = TimelineEvent.objects.get(id=data['timeline'])
        else:
            currentArticle.timeline = None
        currentArticle.save()
        request.method = ""
        return articleEdit(request,category,slg)
    else:
        currentFormSet = ImageFormSet(initial=currentGallery)
        returnForm['currentFormSet'] = currentFormSet
        returnForm['currentArticle'] = currentArticle
        returnForm['currentCategory'] = currentArticle.category
        returnForm['currentNumero'] = currentArticle.numero
        returnForm['currentAuthors'] = currentArticle.author.all()
        msg = "Edit article <b>" + str(currentArticleContent) + "</b>'s information. <a href=/"+str(currentArticle.category)+"/article/"+currentArticle.slg+"/edit> Back to edit article </a>"
        numeros = Numero.objects.all()
        categories = CategoryDetail.objects.filter(language=language)
        users = UserProfile.objects.all()
        returnForm['categories'] = categories
        returnForm['users'] = users
        returnForm['edito'] = currentArticle.edito
        returnForm['headline'] = currentArticle.headline
        try:
            returnForm['timeline'] = currentArticle.timeline.id
            eventDetail = currentArticle.timeline.detail.get(language=language)
            returnForm['timelineDetail'] = currentArticle.timeline.start.strftime('%Y-%m-%d') + " " + eventDetail.content
        except:
            returnForm['timeline'] = 0
            returnForm['timelineDetail'] = "Null"
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
    returnForm, language = init(request)
    if request.method == 'POST':
        a = Article.objects.get(slg=slg)
        article = a.article.get(language=language)
        article.status = 2
        article.save()
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
        data = json.loads(request.body.decode('utf-8'))
        if data['action']=="delete":
            event = TimelineEvent.objects.get(id=data['id'])
            event.delete()
        elif data['action']=='add':
            newEvent = TimelineEvent.objects.create(start=data['start'])
            try:
                newEvent.end = data['end']
            except:
                pass
            newEvent.save()
            newEventDetail = TimelineEventDetail.objects.create(content=data['content'],language=language)
            newEventDetail.event = newEvent
            newEventDetail.save()
            d={}
            d['id'] = newEvent.id;
            return  HttpResponse(json.dumps(d), content_type="application/json")

        elif data['action']=='edit':
            eventSelected = TimelineEvent.objects.get(id=data['id'])
            eventSelectedDetail = eventSelected.detail.get(language=language)
            eventSelected.start = data['start']
            try:
                eventSelected.end = data['end']
            except:
                pass
            eventSelected.save()
            eventSelectedDetail.content = data['content']
            eventSelectedDetail.save()

        # for event in data:
        #     if event['action'] == 'delete':
        #         tmp = TimelineEvent.objects.get(id=event['id'])
        #         print(tmp)
        #         tmp.delete()
        #     else:
        #         if event['id']=='new':
        #         else:
    return HttpResponseRedirect('/')
