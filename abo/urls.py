from django.conf.urls import  url
from abo import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^client/(?P<client>[0-9]+)$', views.clientDetail, name='clientDetail'),
    url(r'^client/(?P<client>[0-9]+)/edit$', views.clientEdit, name='clientEdit'),
    url(r'^search_client$', views.searchClient, name='searchClient'),
    url(r'^adress_pdf', views.genAdressPDF, name='genAdressPDF'),
]
