from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length = 128, blank = True)

    def __str__(self):
        return self.user.username

class Article(models.Model):
    author = models.ForeignKey(UserProfile, null=True)
    date = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    

class ArticleContent(models.Model):
    LANGUAGES = (
        ('fr', 'Français'),
        ('tw', '繁體中文'),
    )
    title = models.CharField(max_length=128)
    content = models.TextField(null=True)
    language = models.CharField(max_length=2, choices=LANGUAGES, default='fr')


    def __str__(self):
        return self.title