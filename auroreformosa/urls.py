from django.conf.urls import  url
from auroreformosa import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about', views.about, name='about'),
    url(r'^login/$', views.userLogin, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^abonnement', views.abonnement, name="abonnement"),
    url(r'^contact', views.contact, name="contact"),
    url(r'^createuser', views.createUser, name="createuser"),
    url(r'^upload', views.uploadImg, name='upload'),
    url(r'^createarticle', views.createarticle, name='createarticle'),
    url(r'^createcomic', views.createComic, name='createComic'),
    url(r'^session_language/$', views.session_language, name='session_language'),
    url(r'^comics/(?P<slg>.+)$', views.comics, name="comics"),
    url(r'^(?P<category>[a-z]+)/$', views.category, name='category'),
    url(r'^(?P<category>[a-z]+)/article/(?P<slg>.+)$', views.article, name='article'),
    url(r'^no/(?P<numero>[0-9.]+)$', views.archive, name='archive'),
    url(r'^no/edit$', views.archiveEdit, name='archiveEdit'),
]
