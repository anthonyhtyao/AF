from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Subscriber(models.Model):
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
    amount = models.IntegerField(default=0)
    received = models.BooleanField(default=False)
    receipt = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1)
    auditor = models.ForeignKey(User,null=True)

class Subscription(models.Model):
    PAYMENT = {('Y','Yes'),('N','No'),('P','Point'),('E','Exempte')}
    subscriber = models.ForeignKey(Subscriber, related_name='subscriptions')
    start = models.IntegerField()
    end = models.IntegerField()
    quantity = models.IntegerField(default=1)
    payment = models.CharField(max_length=1, choices=PAYMENT, default='N')
    status = models.SmallIntegerField(default=1)
    auditor = models.ForeignKey(User,null=True)
