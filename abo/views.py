from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.template.loader import get_template
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from abo.models import *
import json
from django.forms.models import model_to_dict

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

@login_required
def clientEdit(request,client):
    client = Subscriber.objects.get(id=int(client))
    if request.method=="POST":
        data = json.loads(request.body.decode('utf-8'))
        client.email = data['clientEmail']
        client.adress = data['clientAdress']
        client.info = 1 == data['clientInfo']
        client.remark = data['clientRemark']
        client.save()
        return HttpResponse(1)
