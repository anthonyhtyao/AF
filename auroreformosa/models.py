from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length = 128, blank = True)

    def __str__(self):
        return self.user.username

class Img(models.Model):
    imgfile = models.FileField(upload_to='img')
    title = models.CharField(max_length=256, null=True)

    def __str__(self):
        return self.title

class Numero(models.Model):
    numero = models.FloatField()
    image = models.ForeignKey(Img, null=True)
    titleFR = models.CharField(max_length=128, null=True)
    titleTW = models.CharField(max_length=128, null=True)

    def __str__(self):
        if self.numero - int(self.numero) == 0:
            return str(int(self.numero))
        else:
            return str(self.numero)

class Category(models.Model):
    category = models.CharField(max_length = 20)
    color = models.CharField(max_length = 20, default="#FF0033")

    def __str__(self):
        return self.category

class Tag(models.Model):
    tag = models.CharField(max_length = 20)
    recipe = models.BooleanField(default = False)

    def __str__(self):
        return self.tag

# field image is the head image of article
# field gallery store all images of this article, can be null
# one edito and one headline for each numero, an article cannot be edito and headline in same time
class Article(models.Model):
    author = models.ForeignKey(UserProfile, null = True)
    date = models.DateTimeField(auto_now_add = True, auto_now = False, null = True)
    category = models.ForeignKey(Category, related_name="article", null=True)
    numero = models.ForeignKey(Numero, null=True, related_name="article", blank = True)
    title = models.CharField(max_length=128, unique=True)
    slg = models.SlugField()
    image = models.ForeignKey(Img, null = True, blank=True)
    gallery = models.ManyToManyField(Img, blank=True, related_name="galleryAricle")
    edito = models.BooleanField(default=False)
    headline = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slg = slugify(self.title)
        super(Article, self).save(*args, **kwargs)

# Return True if language given for this article exists 
    def languageIsExist(self, language):
        b = False
        try:
            b = b or self.article.filter(language=language).count() == 1
        except:
            pass
        try:
            b = b or self.comic.filter(language=language).count() == 1
        except:
            pass
        return b

class ArticleContent(models.Model):
    LANGUAGES = (
        ('fr', 'Français'),
        ('tw', '繁體中文'),
    )
    article = models.ForeignKey(Article, null = True, related_name='article')
    title = models.CharField(max_length = 128)
    abstract = models.TextField(null = True, blank=True)
    content = models.TextField(null = True)
    language = models.CharField(max_length = 2, choices = LANGUAGES, default = 'fr')

    def inCategory(self,category):
        return self.article.category == category

    def inNumero(self, numero):
        return self.article.numero == numero

    def __str__(self):
        return self.title

class Comic(models.Model):
    LANGUAGES = (
        ('fr', 'Français'),
        ('tw', '繁體中文'),
    )
    article = models.ForeignKey(Article, null = True, related_name='comic')
    title = models.CharField(max_length = 128)
    image = models.ForeignKey(Img, null=True)
    content = models.TextField(null = True, blank=True)
    language = models.CharField(max_length = 2, choices = LANGUAGES, default = 'fr')

    def __str__(self):
        return self.title

class CategoryDetail(models.Model):
    LANGUAGES = (
        ('fr', 'Français'),
        ('tw', '繁體中文'),
    )
    category = models.ForeignKey(Category, null = True, related_name="detail")
    title = models.CharField(max_length = 20)
    language = models.CharField(max_length = 2, choices = LANGUAGES, default = 'fr')

    def __str__(self):
        return self.title

class TagDetail(models.Model):
    LANGUAGES = (
        ('fr', 'Français'),
        ('tw', '繁體中文'),
    )
    tag = models.ForeignKey(Tag, null = True, related_name="detail")
    title = models.CharField(max_length = 20)
    language = models.CharField(max_length = 2, choices = LANGUAGES, default = 'fr')

    def __str__(self):
        return self.title
