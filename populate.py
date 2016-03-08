import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AF.settings')

import django
django.setup()

from auroreformosa.models import *

def populate():
	add_category('history', 'Histoire', '歷史')
	add_category('culture', 'Culture', '文化')
	add_category('politic', 'Politique', '政治')
	add_category('society', 'Société', '社會')
	add_category('recipe', 'Recette', '食譜')
	add_category('art', 'Art', '藝術')
	add_category('news', 'Nouvelles', '最新消息')

def add_category(category_, category_fr, category_tw):
	c = Category.objects.get_or_create(category = category_)
	c[0].save()

	c_tw = CategoryDetail.objects.get_or_create(title=category_tw)
	c_tw[0].category=c[0]
	c_tw[0].language='tw'
	c_tw[0].save()
	
	c_fr = CategoryDetail.objects.get_or_create(title=category_fr)
	c_fr[0].category=c[0]
	c_fr[0].language='fr'
	c_fr[0].save()


if __name__=='__main__':
	populate()
	print('okey')