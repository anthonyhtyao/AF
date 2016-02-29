from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    name_fr = models.CharField(max_length = 128, blank = True)
    name_tw = models.CharField(max_length = 128, blank = True)

    def __str__(self):
        return self.user.username

class Article(models.Model):
    title_fr = models.CharField(max_length=128)
    title_tw = models.CharField(max_length=128)
    author = models.ForeignKey(UserProfile)
    content_fr = models.TextField(null=True)
    content_tw = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return self.title_fr