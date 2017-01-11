from django.conf.urls import  url
from abo import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^client/(?P<client>[0-9]+)$', views.clientDetail, name='clientDetail'),
]
