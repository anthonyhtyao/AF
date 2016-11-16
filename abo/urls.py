from django.conf.urls import  url
from abo import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]
