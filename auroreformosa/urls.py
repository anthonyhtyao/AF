from django.conf.urls import  url
from auroreformosa import views

urlpatterns = [
        url(r'^$', views.index, name='index'),
]
