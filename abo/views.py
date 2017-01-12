from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.template.loader import get_template
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from abo.models import *

@login_required
def index(request):
    returnForm = {}
    
    return render(request, 'abo/index.html',{})

@login_required
def clientDetail(request,client):
    returnForm = {}
    client = Subscriber.objects.get(id=int(client))
    dons = Donation.objects.filter(donor=client)
    subs = Subscription.objects.filter(subscriber=client)
    returnForm['client'] = client
    returnForm['dons'] = dons
    returnForm['subs'] = subs
    return render(request, 'abo/clientDetail.html',returnForm)
