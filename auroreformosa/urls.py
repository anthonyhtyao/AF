from django.conf.urls import patterns, url
from auroreformosa import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'))