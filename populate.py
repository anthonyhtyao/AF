import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AF.settings')

import django
django.setup()

from auroreformosa.models import *

def populate():
    category()

def category():
    add_category('history', 'Histoire', '歷史')
    add_category('culture', 'Culture', '文化')
    add_category('politic', 'Politique', '政治')
    add_category('society', 'Société', '社會')
    add_category('recipe', 'Recette', '食譜')
    add_category('art', 'Art', '藝術')
    add_category('news', 'Nouvelles', '最新消息')
    add_category('edito', 'edito', '編者言')
    add_category('comics', 'Bande dessinée', '漫畫')

def add_category(category_, category_fr, category_tw):
	[c,c_bool] = Category.objects.get_or_create(category = category_)
	c.save()

	[c_tw, c_tw_bool] = CategoryDetail.objects.get_or_create(title=category_tw)
	c_tw.category=c
	c_tw.language='tw'
	c_tw.save()
	
	[c_fr, c_fr_bool] = CategoryDetail.objects.get_or_create(title=category_fr)
	c_fr.category=c
	c_fr.language='fr'
	c_fr.save()


if __name__=='__main__':
	populate()
	print('okey')
