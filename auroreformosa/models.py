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
        return self.numero

class Category(models.Model):
    TITLES = (
        ('Politique', 'Politique'),
        ('Recette', 'Recette'),
        ('Societe', 'Société'),
        ('Arts', 'Arts'),
        ('Culture', 'Culture'),
        ('Jeux', 'Jeux de mots'),
        ('Dessin', 'Bande dessinée'),
        ('Vies', 'Vies-à-vies'),
        ('Actualite', 'Actualité')
    )
    title = models.CharField(max_length = 10, choices = TITLES)

    def __str__(self):
        return self.title

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
    content = models.TextField(null = True)
    language = models.CharField(max_length = 2, choices = LANGUAGES, default = 'fr')


    def __str__(self):
        return self.title

class CategoryDetail(models.Model):
    LANGUAGES = (
        ('fr', 'Français'),
        ('tw', '繁體中文'),
    )
    TITLES = (
        ('Politique', 'Politique'),
        ('Recette', 'Recette'),
        ('Societe', 'Société'),
        ('Arts', 'Arts'),
        ('Culture', 'Culture'),
        ('Jeux', 'Jeux de mots'),
        ('Dessin', 'Bande dessinée'),
        ('Vies', 'Vies-à-vies'),
        ('Actualite', 'Actualité')
    )
    category = models.ForeignKey(Category)
    title = models.CharField(max_length = 10, choices = TITLES)
    language = models.CharField(max_length = 2, choices = LANGUAGES, default = 'fr')

    def __str__(self):
        return self.title
