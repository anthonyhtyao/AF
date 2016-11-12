from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from PIL import Image
from django.conf import settings
# Create your models here.



class UserProfile(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(max_length = 128, blank = True)

    def __str__(self):
        return self.name

class Img(models.Model):
    imgfile = models.FileField(upload_to='img')
    imgfile_m = models.FileField(upload_to='img/middle', null=True, blank=True)
    imgfile_s = models.FileField(upload_to='img/small', null=True, blank=True)
    title = models.CharField(max_length=256, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Save Photo after ensuring it is not blank.  Resize as needed.
        """
        super(Img, self).save(*args, **kwargs)
        url = self.imgfile.url
        image = Image.open(url[1:])
        width, height = image.size
        if width/height >= 1:
            size = (1280,1280)
            size_m = (700,700)
            size_s = (300,300)
        else:
            size = (1000,1000)
            size_m = (500,500)
            size_s = (200,200)

        image.thumbnail(size, Image.ANTIALIAS)
        image.save(url[1:])
        url_m = self.imgfile_m.url
        image_m = Image.open(url[1:])
        image_m.thumbnail(size_m, Image.ANTIALIAS)
        image_m.save(url_m[1:])
        url_s = self.imgfile_s.url
        image_s = Image.open(url_s[1:])
        image_s.thumbnail(size_s, Image.ANTIALIAS)
        image_s.save(url_s[1:])

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
    order = models.IntegerField(default="0")

    def __str__(self):
        return self.category

class Tag(models.Model):
    tag = models.CharField(max_length = 20)
    recipe = models.BooleanField(default = False)

    def __str__(self):
        return self.tag

class TimelineEvent(models.Model):
    start = models.DateField()
    end = models.DateField(null=True, blank=True)

    def __str__(self):
        return "Timeline event at " + self.start.strftime('%Y-%m-%d')

# field image is the head image of article
# field gallery store all images of this article, can be null
# one edito and one headline for each numero, an article cannot be edito and headline in same time
# There are three status for an article. 0 = deleted, 1 = editting(default) and 2 = published
class Article(models.Model):
    author = models.ManyToManyField(UserProfile)
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
    timeline = models.ForeignKey(TimelineEvent,null=True,blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slg = slugify(self.title)
        super(Article, self).save(*args, **kwargs)

# Return True if language given for this article exists
    def languageIsExist(self, language):
        b = False
        try:
            b = b or self.article.exclude(status=0).filter(language=language).count() == 1
        except:
            pass
        try:
            b = b or self.comic.exclude(status=0).filter(language=language).count() == 1
        except:
            pass
        return b
# Status = 0 if content is deleted
# Status = 1 if content is editting
# Status = 2 if content is pubic
class ArticleContent(models.Model):
    article = models.ForeignKey(Article, null = True, related_name='article')
    title = models.CharField(max_length = 128)
    abstract = models.TextField(null = True, blank=True)
    content = models.TextField(null = True)
    status = models.SmallIntegerField(default = 1)
    language = models.CharField(max_length = 2, choices = settings.LANGUAGES, default = 'fr')

    def inCategory(self,category):
        return self.article.category == category

    def inNumero(self, numero):
        return self.article.numero == numero

    def __str__(self):
        return self.title

class Comic(models.Model):
    article = models.ForeignKey(Article, null = True, related_name='comic')
    title = models.CharField(max_length = 128)
    image = models.ForeignKey(Img, null=True)
    content = models.TextField(null = True, blank=True)
    status = models.SmallIntegerField(default = 2)
    language = models.CharField(max_length = 2, choices = settings.LANGUAGES, default = 'fr')

    def __str__(self):
        return self.title

class CategoryDetail(models.Model):
    category = models.ForeignKey(Category, null = True, related_name="detail")
    title = models.CharField(max_length = 20)
    language = models.CharField(max_length = 2, choices = settings.LANGUAGES, default = 'fr')

    def __str__(self):
        return self.title

class TagDetail(models.Model):
    tag = models.ForeignKey(Tag, null = True, related_name="detail")
    title = models.CharField(max_length = 20)
    language = models.CharField(max_length = 2, choices = settings.LANGUAGES, default = 'fr')

    def __str__(self):
        return self.title

class TimelineEventDetail(models.Model):
    event = models.ForeignKey(TimelineEvent, null = True, related_name="detail")
    content = models.CharField(max_length = 20)
    language = models.CharField(max_length = 2, choices = settings.LANGUAGES, default = 'fr')

    def __str__(self):
        return self.language + " " + self.content
