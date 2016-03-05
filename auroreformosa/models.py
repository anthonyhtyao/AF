from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length = 128, blank = True)

    def __str__(self):
        return self.user.username
class Numero(models.Model):
    numero = models.PositiveIntegerField()

    def __str__(self):
        return str(self.numero)

class Category(models.Model):
    category = models.CharField(max_length = 20)

    def __str__(self):
        return self.category

class Article(models.Model):
    author = models.ForeignKey(UserProfile, null = True)
    date = models.DateTimeField(auto_now_add = True, auto_now = False, null = True)
    category = models.ForeignKey(Category)
    numero = models.ForeignKey(Numero, null=True)

class ArticleContent(models.Model):
    LANGUAGES = (
        ('fr', 'Français'),
        ('tw', '繁體中文'),
    )
    article = models.ForeignKey(Article, null = True)
    title = models.CharField(max_length = 128)
    abstract = models.TextField(null = True)
    content = models.TextField(null = True)
    language = models.CharField(max_length = 2, choices = LANGUAGES, default = 'fr')

    def inCategory(self,category):
        return self.article.category == category

    def __str__(self):
        return self.title

class CategoryDetail(models.Model):
    LANGUAGES = (
        ('fr', 'Français'),
        ('tw', '繁體中文'),
    )
    category = models.ForeignKey(Category)
    title = models.CharField(max_length = 20)
    language = models.CharField(max_length = 2, choices = LANGUAGES, default = 'fr')

    def __str__(self):
        return self.title

class Img(models.Model):
    imgfile = models.FileField(upload_to='img')
