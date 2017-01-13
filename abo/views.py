from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.template.loader import get_template
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from abo.models import *
import json
from django.forms.models import model_to_dict
from auroreformosa.models import Numero
from django.db.models import Max, Sum
from operator import itemgetter

currentNo = int(Numero.objects.all().aggregate(Max('numero'))['numero__max'])

@login_required
def index(request):
    returnForm = {}
    
    clientsLst = Subscriber.objects.all()
    clients = []
    for client in clientsLst:
        tmp={'id':client.id,'name':client.name,'family_name':client.family_name,'email':client.email}
        tmp['don']=int(client.donations.aggregate(Sum('amount'))['amount__sum'] or 0)
        tmp['end']=int(client.subscriptions.aggregate(Max('end'))['end__max'] or 0)
        clients.append(tmp)
    returnForm['clients'] = sorted(clients, key=itemgetter('end'),reverse=True)
    return render(request, 'abo/index.html',returnForm)

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
