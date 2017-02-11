from django.conf.urls import  url
from abo import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^client/(?P<client>[0-9]+)$', views.clientDetail, name='clientDetail'),
    url(r'^client/(?P<client>[0-9]+)/edit$', views.clientEdit, name='clientEdit'),
    url(r'^client/(?P<client>[0-9]+)/sub_delete', views.subDelete, name='subDelete'),
    url(r'^client/(?P<client>[0-9]+)/sub_add', views.subAdd, name='subAdd'),
    url(r'^client/(?P<client>[0-9]+)/sub_edit', views.subEdit, name='subEdit'),
    url(r'^client/(?P<client>[0-9]+)/don_add', views.donAdd, name='donAdd'),
    url(r'^client/(?P<client>[0-9]+)/don_delete', views.donDelete, name='donDelete'),
    url(r'^client/(?P<client>[0-9]+)/don_edit', views.donEdit, name='donEdit'),
    url(r'^search_client$', views.searchClient, name='searchClient'),
    url(r'^adress_pdf', views.genAdressPDF, name='genAdressPDF'),
    url(r'^add_client', views.addClient, name='addClient'),
]
