from django.conf.urls import  url
from auroreformosa import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about', views.about, name='about'),
    url(r'^upload', views.uploadImg, name='upload'),
    url(r'^createarticle', views.createarticle, name='createarticle'),
    url(r'^session_language/$', views.session_language, name='session_language'),
    url(r'^comics/(?P<slg>.+)$', views.comics, name="comics"),
    url(r'^(?P<category>[a-z]+)/$', views.category, name='category'),
    url(r'^(?P<category>[a-z]+)/article/(?P<slg>.+)$', views.article, name='article')
]
