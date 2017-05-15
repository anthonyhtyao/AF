from django.db import models
from django.contrib.auth.models import User
import random
import string

def genRandomID(n):
    s = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))
    return s

# Create your models here.
class Subscriber(models.Model):
    owner = models.OneToOneField(User, null=True, blank=True)
    CIVILITE = {('Ms','M.'),('Ml','Mlle'),('Mm','Mme')}
    civilite = models.CharField(max_length=2, choices=CIVILITE, default='Ms')
    family_name = models.CharField(max_length=63)
    name = models.CharField(max_length=63)
    email = models.EmailField(max_length=127, null=True)
    adress = models.TextField()
    country = models.CharField(max_length=63)
    info = models.BooleanField(default=False)
    remark = models.CharField(max_length=128)

    def __str__(self):
        return self.name + " " + self.family_name

class Donation(models.Model):
    donor = models.ForeignKey(Subscriber, related_name='donations')
    rid = models.CharField(max_length=5)
    createdtime = models.DateTimeField(auto_now_add = True, auto_now = False)
    receivedtime = models.DateTimeField(null=True, blank=True)
    amount = models.IntegerField(default=0)
    received = models.BooleanField(default=False)
    receipt = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1)
    auditor = models.ForeignKey(User,null=True)

    def save(self, *args, **kwargs):
        if not self.rid:
            self.rid = genRandomID(5)
        super(Donation, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.amount) + " created at " + self.createdtime.strftime('%Y-%m-%d')

class Subscription(models.Model):
    PAYMENT = {('N','No'),('Y','Yes'),('P','Point'),('E','Exempte')}
    subscriber = models.ForeignKey(Subscriber, related_name='subscriptions')
    rid = models.CharField(max_length=8)
    createdtime = models.DateTimeField(auto_now_add = True, auto_now = False)
    receivedtime = models.DateTimeField(null=True, blank=True)
    start = models.IntegerField()
    end = models.IntegerField()
    quantity = models.IntegerField(default=1)
    payment = models.CharField(max_length=1, choices=PAYMENT, default='N')
    status = models.SmallIntegerField(default=1)
    auditor = models.ForeignKey(User,null=True)

    def save(self, *args, **kwargs):
        if not self.rid:
            self.rid = genRandomID(8)
        super(Subscription, self).save(*args, **kwargs)

    def __str__(self):
        return self.rid + " created at " + self.createdtime.strftime('%Y-%m-%d')
