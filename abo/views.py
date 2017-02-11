from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.template.loader import get_template
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from abo.models import *
import json
from django.forms.models import model_to_dict
from auroreformosa.models import Numero
from django.db.models import Max, Sum
from operator import itemgetter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.core.urlresolvers import reverse
from abo.forms import *
from django.template.defaultfilters import slugify

currentNo = int(Numero.objects.all().aggregate(Max('numero'))['numero__max'])

def isStaff(user):
    return user.is_staff

@login_required
def index(request):
    returnForm = {}
    
    clientsLst = Subscriber.objects.all()
    clients = transFormClients(clientsLst)
    returnForm['clients'] = sorted(clients, key=itemgetter('end'),reverse=True)
    return render(request, 'abo/index.html',returnForm)

@login_required
def clientDetail(request,client):
    returnForm = {}
    client = Subscriber.objects.get(id=int(client))
    dons = Donation.objects.filter(donor=client,status__gt=0)
    subs = Subscription.objects.filter(subscriber=client,status__gt=0)
    returnForm['client'] = client
    returnForm['dons'] = dons
    returnForm['subs'] = subs
    returnForm['PAYMENT'] = Subscription.PAYMENT
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

@login_required
def subDelete(request,client):
    if request.method=="POST":
        data = json.loads(request.body.decode('utf-8'))
        subID = data['subID']
        sub = Subscription.objects.get(id=subID)
        assert int(client) == sub.subscriber.id
        sub.status = 0
        sub.save()
        return HttpResponse(1)

@login_required
def subAdd(request,client):
    if request.method=="POST":
        client = Subscriber.objects.get(id=int(client))
        data = json.loads(request.body.decode('utf-8'))
        data['subscriber'] = client
        Subscription.objects.create(**data)
        return HttpResponse(1)

@login_required
def subEdit(request,client):
    if request.method=="POST":
        data = json.loads(request.body.decode('utf-8'))
        subID = data.pop('id',None)
        sub = Subscription.objects.get(id=subID)
        assert int(client) == sub.subscriber.id
        for key,value in data.items():
            setattr(sub,key,value)
        sub.save()
        return HttpResponse(1)

@login_required
def donAdd(request,client):
    if request.method=="POST":
        client = Subscriber.objects.get(id=int(client))
        data = json.loads(request.body.decode('utf-8'))
        data['donor'] = client
        Donation.objects.create(**data)
        return HttpResponse(1)

@login_required
def donDelete(request,client):
    if request.method=="POST":
        data = json.loads(request.body.decode('utf-8'))
        donID = data['donID']
        don = Donation.objects.get(id=donID)
        assert int(client) == don.donor.id
        don.status = 0
        don.save()
        return HttpResponse(1)

@login_required
def donEdit(request,client):
    if request.method=="POST":
        data = json.loads(request.body.decode('utf-8'))
        donID = data.pop('id',None)
        don = Donation.objects.get(id=donID)
        assert int(client) == don.donor.id
        for key,value in data.items():
            setattr(don,key,value)
        don.save()
        return HttpResponse(1)
    
@login_required
def searchClient(request):
    if request.method == "GET":
        data = request.GET
        containsLst = ['email','family_name','name','country','info']
        filterSet = {}
        excludeSet={}
        for o in containsLst:
            try:
                v = data[o]
                filterSet[o+'__icontains'] = v
            except:
                pass
        ### Payment filter
        try:
            assert data['payment'] == '1'
            filterSet['subscriptions__payment'] = 'N'
        except:
            pass
        ### Numero filter
        try:
            numero = int(float(data['numero']))
            filterSet['subscriptions__start__lte'] = numero
            filterSet['subscriptions__end__gte'] = numero
        except:
            pass
        ### Expire filter
        try:
            assert data['expire'] == '1'
            excludeSet['subscriptions__end__gte'] = currentNo
        except:
            pass
        clientsLst = Subscriber.objects.filter(**filterSet).exclude(**excludeSet).order_by('id')
        clients = transFormClients(clientsLst) 
        return render(request, 'abo/indexTable.html',{'clients':clients})

def transFormClients(clientsLst):
    clients = []
    for client in clientsLst:
        tmp={'id':client.id,'name':client.name,'family_name':client.family_name,'email':client.email}
        tmp['don']=int(client.donations.aggregate(Sum('amount'))['amount__sum'] or 0)
        tmp['end']=int(client.subscriptions.aggregate(Max('end'))['end__max'] or 0)
        clients.append(tmp)
    return clients

@user_passes_test(isStaff)
def genAdressPDF(request):
    if request.method=="POST":
        data = json.loads(request.POST['clientsLst'])
        clients = Subscriber.objects.filter(pk__in=data['clientsLst']).order_by('id')

        # Create the HttpResponse object with the appropriate PDF headers.
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="adress.pdf"'
        maxWidth, maxHeight = A4
        lineSpacing = 15
        rows = 7
        rowHeight = 115
        lines = [(maxWidth/2,maxHeight,maxWidth/2,0)]
        for i in range(rows-1):
            lines.append((0,maxHeight-15-rowHeight*(i+1),maxWidth,maxHeight-15-rowHeight*(i+1)))
            # Create the PDF object, using the response object as its "file."
        p = canvas.Canvas(response) 
        # PageInit
        def pageInit():
            p.setFont('Courier',10)
            p.setDash(2,4)
            p.lines(lines)

        pageInit()
     
        ind = 0
        # Draw information for each client
        for client in clients:
            q = client.subscriptions.filter(start__lte=currentNo,end__gte=currentNo).aggregate(Sum('quantity'))['quantity__sum']
            if not q:
                q = 0
            expire = bool(client.subscriptions.filter(end__gt=currentNo).aggregate(Sum('quantity'))['quantity__sum'])
            
            indP = ind%(rows*2)
            if ind != 0 and indP == 0:
                p.showPage()
                pageInit()

            w = 50+maxWidth/2*(indP%2)
            h = maxHeight-30-rowHeight*(indP//2)
            indL = 0
            p.drawString(w, h-lineSpacing*indL, "Client ID : "+str(client.id)+" expire: "+str(not expire)+" QT: "+str(q))
            indL += 1
            p.drawString(w, h-lineSpacing*indL, client.get_civilite_display()+" "+client.name+" "+client.family_name.upper())
            indL += 1
            adressLst = client.adress.splitlines()
            for adress in adressLst:
                p.drawString(w, h-lineSpacing*indL, adress)
                indL += 1
            p.drawString(w, h-lineSpacing*indL, client.country)
            ind += 1
        p.showPage()
        p.save()
        return response

@login_required
def addClient(request):
    returnForm = {'CIVI':Subscriber.CIVILITE}
    if request.method=='POST':
        form = ClientForm(request.POST)
        print(form)
        if form.is_valid():
            client = form.save()
            username = request.POST['username']
            email = request.POST['email']
            u = User.objects.create_user(username,email)
            client.owner = u
            client.save()
            return HttpResponseRedirect(reverse('clientDetail', args=(client.id,)))
    return render(request,'abo/addClient.html',returnForm)
