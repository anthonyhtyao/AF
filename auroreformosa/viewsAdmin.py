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
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from auroreformosa.views import *
from django.forms.models import formset_factory
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.conf import settings
from operator import itemgetter

def isStaff(user):
    return user.is_staff

def getUsersLst(user,article=None):
    if user.is_staff:
        users = UserProfile.objects.all().order_by('name')
        return users
    try:
        return article.author.all()
    except:
        return [user]

@user_passes_test(isStaff)
def uploadImg(request):
    returnForm, language = init(request)
    returnForm = setMsg(returnForm)
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
@permission_required('auroreformosa.add_article')
def createComic(request, errMsg="", msg="", warnMsg=""):
    returnForm, language = init(request)
    returnForm = setMsg(returnForm)
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
                    return createComic(request, msg="Commics FR and TW added successfully. <a class='FR' href=/comics/"+article.slg+"> Click to read Comic FR </a> and <a class='TW' href=/comics/"+article.slg+"> Click to read Comic TW </a>")
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
    returnForm['msg'] = msg
    return render(request, 'admin/createComic.html', returnForm)

@login_required
@permission_required('auroreformosa.change_article')
def comicsEdit(request, slg, errMsg="", msg="", warnMsg=""):
    returnForm, language = init(request)
    returnForm = setMsg(returnForm)
    articleParent = Article.objects.get(slg=slg)
    try:
        assert request.user.is_staff or request.user.userprofile in articleParent.authors
    except:
        return HttpResponseRedirect(reverse('comics', args=(slg,)))
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

    returnForm['currentNumero'] = articleParent.numero
    returnForm['authors'] = articleParent.author.all()
    returnForm['form'] = comicForm
    returnForm['users'] = users
    returnForm['errMsg'] = errMsg
    returnForm['warnMsg'] = warnMsg
    returnForm['msg'] = msg
    return render(request, 'admin/createComic.html', returnForm)

# Set article's status to 1 (article editting) and go to preview page if success
@login_required
@permission_required('auroreformosa.add_article')
def createarticle(request, errMsg="", msg=""):
    currentUser = request.user
    returnForm, language = init(request)
    returnForm = setMsg(returnForm)
    # Gallery is a imgform set
    ImageFormSet = formset_factory(form=ImgForm, extra = 3, max_num=10)
    if request.method == 'POST':
        data = request.POST
        form = ArticleForm(request.POST)
        formset = ImageFormSet(data, request.FILES)
        if form.is_valid() and formset.is_valid():
            currentArticle = Article.objects.create(title=data['title'])
            try:
                success, label = updateArticle(True,currentArticle,data,formset,request.FILES)
                if not success:
                    currentArticle.delete()
                    request.method = ""
                    return createarticle(request,errMsg=label)
                else:
                    articleContent = form.save()
                    articleContent.article = currentArticle
                    articleContent.status = 1
                    articleContent.save()
                    #Return article preview page
                    request.session['language'] = data['language']
                    return HttpResponseRedirect(reverse('articlePreview', args=(str(currentArticle.category),currentArticle.slg,)))
            except:
                pass
    articleForm = ArticleForm()
    numeros = Numero.objects.all()
    categoryFR = CategoryDetail.objects.filter(language='fr')
    categoryTW = CategoryDetail.objects.filter(language='tw')
    returnForm['users'] = getUsersLst(currentUser)
    # Get no version details by get request
    try:
        no = request.GET['no']
    except:
        no = 1
    returnForm['selectedLang'] = language
    returnForm['formset'] = ImageFormSet
    returnForm['currentNumero'] = float(no)
    returnForm['form'] = articleForm
    returnForm['categoryFR'] = categoryFR
    returnForm['categoryTW'] = categoryTW
    return render(request, 'admin/createArticle.html', returnForm)

@user_passes_test(isStaff)
def archiveEdit(request):
    returnForm, language = init(request)
    returnForm = setMsg(returnForm)
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
                    comicFR = a.comic.exclude(status=0).get(language="fr")
                    d["comicFR"] = comicFR
                except:
                    d["comicFR"] = ""
                try:
                    comicTW = a.comic.exclude(status=0).get(language="tw")
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

@user_passes_test(isStaff)
def createUser(request, msg=""):
    returnForm,language = init(request)
    returnForm = setMsg(returnForm)
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
@permission_required('auroreformosa.change_article')
def articleEdit(request, category, slg, errMsg="", msg=""):
    returnForm, language = init(request)
    returnForm = setMsg(returnForm)
    currentArticle = Article.objects.get(slg=slg)
    try:
        assert request.user.is_staff or (request.user.userprofile in currentArticle.author.all())
    except:
        return HttpResponseRedirect(reverse('article', args=(category,slg,)))
    
    ImageFormSet = formset_factory(form=ImgForm, extra=3, max_num=10)
    selectedLang = request.GET.get('lang',language)
    try:
        returnForm = getArticleInfo(slg,returnForm,selectedLang)
    except:
        return HttpResponseRedirect('/')
    if not selectedLang in [ a[0] for a in settings.LANGUAGES]:
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        data = request.POST
        files = request.FILES
        currentGallery = [{'imgfile':x.imgfile} for x in returnForm['currentGallery']]
        formset = ImageFormSet(data,files,initial=currentGallery)
        success, label = updateArticle(request.user.is_staff,currentArticle,data,formset,files,language=selectedLang)
        if success:
            try:
                articleContent = currentArticle.article.get(language=selectedLang)
            except:
                articleContent = ArticleContent.objects.create(language=selectedLang,title=data['title'],article=currentArticle)
            articleContent.title = data['title']
            articleContent.abstract = data['abstract']
            articleContent.content = data['content']
            articleContent.status = 1
            articleContent.save()
            path = reverse('articlePreview', args=(str(category),slg,),)
            return HttpResponseRedirect(url_with_querystring(path,{'lang':selectedLang}))
    else:
        try:
            returnForm['msg'] += "Edit article <b>" + str(returnForm['currentArticleContent']) + " (Version : " + selectedLang + "). </b>"
        except:
            returnForm['msg'] += "Translate article <b> No. " + str(currentArticle.id) + " (Version : " + selectedLang + "). </b>"
        if currentArticle.article.count() != len(settings.LANGUAGES):
            returnForm['warnMsg'] += "This article's translations aren't completed. <a href='./status'> More detail </a>"
        articleForm = ArticleForm()
        numeros = Numero.objects.all()
        categoryFR = CategoryDetail.objects.filter(language='fr')
        categoryTW = CategoryDetail.objects.filter(language='tw')
        returnForm['selectedLang'] = selectedLang
        returnForm['formset'] = ImageFormSet(initial=[{'imgfile':x.imgfile} for x in returnForm['currentGallery']])
        returnForm['form'] = articleForm
        returnForm['categoryFR'] = categoryFR
        returnForm['categoryTW'] = categoryTW
        returnForm['users'] = getUsersLst(request.user,article=currentArticle)
        returnForm['action'] = 'edit'
        return render(request, 'admin/createArticle.html', returnForm)

@login_required
@permission_required('auroreformosa.change_article')
def articleStatus(request, category, slg, errMsg="", msg=""):
    returnForm, language = init(request)
    returnForm = setMsg(returnForm)
    currentArticle = Article.objects.get(slg=slg)
    try:
        assert request.user.is_staff or request.user.userprofile in currentArticle.author.all()
    except:
        return HttpResponseRedirect(reverse('article', args=(category,slg,)))
    try:
        returnForm = getArticleInfo(slg,returnForm,language)
    except:
        return HttpResponseRedirect('/')
    currentGallery = [{'imgfile':x.imgfile} for x in returnForm['currentGallery']]
    ImageFormSet = formset_factory(form=ImgForm, extra=3, max_num=10)
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        data = request.POST
        files = request.FILES
        formset = ImageFormSet(data,files,initial=currentGallery)
        success, label = updateArticle(request.user.is_staff,currentArticle,data,formset,files,language=language)
        request.method=""
        if success:
            return articleStatus(request, category, slg, msg=label)
        else:
            return articleStatus(request, category, slg, errMsg=label)
    else:
        returnForm["msg"] += "Status of article <b> No. " + str(currentArticle.id) + "</b>."
        articleForm = ArticleForm()
        numeros = Numero.objects.all()
        categoryFR = CategoryDetail.objects.filter(language='fr')
        categoryTW = CategoryDetail.objects.filter(language='tw')
        users = getUsersLst(request.user,article=currentArticle)
        contentStatus = currentArticle.article.values("status","title","language").all()
        statusLst = []
        for lang in settings.LANGUAGES:
            exists = False
            for t in contentStatus:
                if t['language']==lang[0]:
                    exists=True
                    statusLst.append(t)
                    break
            if not exists:
                statusLst.append({'status':0,'title':'','language':lang[0]})
        returnForm['statusLst'] = sorted(statusLst, key=itemgetter('language'))
        returnForm['formset'] = ImageFormSet(initial=currentGallery)
        returnForm['form'] = articleForm
        returnForm['categoryFR'] = categoryFR
        returnForm['categoryTW'] = categoryTW
        returnForm['users'] = users
        returnForm['action'] = 'status'
        returnForm['selectedLang'] = language
        return render(request, 'admin/articleStatus.html', returnForm)

@login_required
def userSettings(request,errMsg="", msg=""):
    returnForm, language = init(request)
    returnForm = setMsg(returnForm)
    currentUser = UserProfile.objects.get(user=request.user)
    if request.method =='POST':
        data = request.POST
        if not request.user.check_password(data['OldPassword']):
            errMsg="Wrong password"
            request.method=""
            return userSettings(request,errMsg=errMsg)
        else:
            request.method=""
            if currentUser.name != data['InputName']:
                currentUser.name = data['InputName']
                currentUser.save()
                msg = "User's name is sucessfully changed. "
            if data['InputPassword1'] != "":
                if data['InputPassword1'] != data['InputPassword2']:
                    errMsg = "These two new passwords don't match"
                    return userSettings(request,errMsg=errMsg, msg=msg)
                else:
                    user = request.user
                    user.set_password(data['InputPassword1'])
                    user.save()
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    msg += "Password is successfully changed."
            return userSettings(request,msg=msg)
    returnForm['currentUser'] = currentUser
    returnForm['errMsg'] = errMsg
    returnForm['msg'] = msg
    return render(request, 'admin/settings.html',returnForm)

@login_required
@permission_required('auroreformosa.add_article')
def articlePreview(request,category,slg):
    returnForm, language = init(request)
    returnForm = setMsg(returnForm)
    selectedLang = request.GET.get('lang',language)
    if request.method == 'POST':
        a = Article.objects.get(slg=slg)
        try:
            tmp = a.article.get(language=selectedLang)
        except:
            return HttpResponseRedirect('/')
        tmp.status = 2
        tmp.save()
        return HttpResponseRedirect(reverse('article', args=(str(a.category),a.slg,)))
    else:
        return article(request,category,slg,status=1,selectedLang=selectedLang)

@login_required
@permission_required('auroreformosa.change_timelineevent')
def timelineEdit(request):
    returnForm, language = init(request)
    returnForm = setMsg(returnForm)
    return render(request, 'admin/timelineEdit.html',returnForm)

@login_required
@permission_required('auroreformosa.add_timelineevent')
def timelineSave(request):
    returnForm, language = init(request)
    returnForm = setMsg(returnForm)
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

@login_required
@permission_required('auroreformosa.add_article')
def articleDelete(request):
    if request.method=="POST":
        data = json.loads(request.body.decode('utf-8'))
        if data['type'] == 'article':
            article = ArticleContent.objects.get(id=data['id'])
            try:
                assert request.user.is_staff or request.user.userprofile in article.authors
            except:
                return HttpResponseRedirect(reverse('article', args=(str(article.category),article.slg,)))
            article.status = 0
            article.save()
        else:
            comic = Comic.objects.get(id=data['id'])
            try:
                assert request.user.is_staff or request.user.userprofile in comic.authors
            except:
                return HttpResponseRedirect(reverse('comics', args=(comic.slg,)))
            comic.status = 0
            comic.save()
        return HttpResponseRedirect('/')
    return HttpResponseRedirect('/')

def setMsg(returnForm):
    returnForm['msg'] = ''
    returnForm['errMsg'] = ''
    returnForm['warnMsg'] = ''
    return returnForm

@login_required
def checkTitleValidity(request):
    if request.method=="GET":
        title = request.GET["title"]
        slg = slugify(title)
        n = Article.objects.filter(slg=slg).count()
        if n==0:
            return HttpResponse(1)
        else:
            return HttpResponse(0)

# Take article's slg and a dictionary and return this dictionary with article's information
# If parameter "lang" is given, add article's content and abstract in dictionary
def getArticleInfo(slg,returnForm,lang=None):
    currentArticle = Article.objects.get(slg=slg)
    if lang:
        try:
            currentArticleContent = currentArticle.article.get(language=lang)
            returnForm['currentArticleContent'] = currentArticleContent
        except:
            pass
    returnForm['currentArticle'] = currentArticle
    returnForm['currentCategory'] = currentArticle.category
    returnForm['currentNumero'] = currentArticle.numero
    returnForm['currentGallery'] = currentArticle.gallery.all()
    returnForm['currentAuthors'] = currentArticle.author.all()
    returnForm['edito'] = currentArticle.edito
    returnForm['headline'] = currentArticle.headline
    try:
        returnForm['timeline'] = currentArticle.timeline.id
        eventDetail = currentArticle.timeline.detail.get(language=lang)
        returnForm['timelineDetail'] = currentArticle.timeline.start.strftime('%Y-%m-%d') + " " + eventDetail.content
    except:
        returnForm['timeline'] = 0
        returnForm['timelineDetail'] = "Null"
    return returnForm

def updateArticle(staff,currentArticle,data,formset,files,language=None):
    numero = Numero.objects.get(id=data['numero'])
    if staff:
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
                return False, "Edito already exists"
        except:
            pass
    try:
        headline = bool(data['isHeadline'])
    except:
        headline = False
    if headline:
        try:
            if numero.article.get(headline=True) != currentArticle:
                return False, "Headline already exists"
        except:
            pass
    try:
        imgTitle = str(files['imgfile']).split("/")[-1]
        img = Img(imgfile = files['imgfile'], imgfile_m = files['imgfile'], imgfile_s = files['imgfile'], title=imgTitle)
        img.save()
        currentArticle.image = img
    except:
        pass
    # Clean article gallery
    currentArticle.gallery.clear()
    print(formset.cleaned_data)
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
    if language:
        lang = language
    else:
        lang = data['language']
    category = Category.objects.get(id=data['category_'+lang])
    currentArticle.numero = numero
    currentArticle.category = category
    currentArticle.edito = edito
    currentArticle.headline = headline
    if data['timeline'] > "0":
        currentArticle.timeline = TimelineEvent.objects.get(id=data['timeline'])
    else:
        currentArticle.timeline = None
    currentArticle.save()
    return True ,"Success"

def url_with_querystring(path, d):
    i = 0
    for key, value in d.items():
        if i == 0:
            path += '?'
        else:
            path += '&'
        path = path + key + '=' + value
        i += 1
    return path

@login_required
@permission_required('auroreformosa.add_article')
def myArticles(request):
    returnForm, language = init(request)
    returnForm = setMsg(returnForm)
    articles = ArticleContent.objects.filter(status__gt = 0,language=language,article__author=request.user.userprofile).order_by('-article__date')
    returnForm['articles'] = articles
    return render(request,'admin/myArticles.html',returnForm)
