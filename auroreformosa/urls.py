from django.conf.urls import  url
from auroreformosa import views, viewsAdmin

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about', views.about, name='about'),
    url(r'^login/$', views.userLogin, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^abonnement', views.abonnement, name="abonnement"),
    url(r'^checktitlevalidity', viewsAdmin.checkTitleValidity, name="checkTitleValidity"),
    url(r'^contact', views.contact, name="contact"),
    url(r'^createuser', viewsAdmin.createUser, name="createuser"),
    url(r'^upload', viewsAdmin.uploadImg, name='upload'),
    url(r'^createarticle', viewsAdmin.createarticle, name='createarticle'),
    url(r'^createcomic', viewsAdmin.createComic, name='createComic'),
    url(r'^session_language/$', views.session_language, name='session_language'),
    url(r'^settings$', viewsAdmin.userSettings, name='userSettings'),
    url(r'^comics/(?P<slg>.+)/edit$', viewsAdmin.comicsEdit, name="comicsEdit"),
    url(r'^comics/(?P<slg>.+)$', views.comics, name="comics"),
    url(r'^timelinedata/$', views.timelinedata, name="timelinedata"),
    url(r'^timeline/edit$', viewsAdmin.timelineEdit, name="timelineEdit"),
    url(r'^timeline/save$', viewsAdmin.timelineSave, name="timelineSave"),
    url(r'^events/(?P<slg>.+)$', views.event, name='event'),
    url(r'^my_articles$', viewsAdmin.myArticles, name="myArticles"),
    url(r'^articlepermit$', viewsAdmin.articlePermit, name="articlePermit"),
    url(r'^article/delete$', viewsAdmin.articleDelete, name="articleDelete"),
    url(r'^(?P<category>[a-z]+)/$', views.category, name='category'),
    url(r'^(?P<category>[a-z]+)/article/(?P<slg>.+)/edit$', viewsAdmin.articleEdit, name='articleEdit'),
    url(r'^(?P<category>[a-z]+)/article/(?P<slg>.+)/preview$', viewsAdmin.articlePreview, name='articlePreview'),
    url(r'^(?P<category>[a-z]+)/article/(?P<slg>.+)/status$', viewsAdmin.articleStatus, name='articleStatus'),
    url(r'^(?P<category>[a-z]+)/article/(?P<slg>.+)$', views.article, name='article'),
    url(r'^author/(?P<slg>[a-z.\-]+)/article$', views.authorArticle, name='authorArticle'),
    url(r'^no/(?P<numero>[0-9.]+)$', views.archive, name='archive'),
    url(r'^no/edit$', viewsAdmin.archiveEdit, name='archiveEdit'),
]
