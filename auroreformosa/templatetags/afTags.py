from django import template

register = template.Library()

@register.filter
def numeroBar(value):
    """Add No. and bar if value no null"""
    if value:
        return "No. "+str(value)+" |"
    else:
        return ""

def numeroNoBar(value):
    """Add No. if value no null"""
    if value:
        return "No. "+str(value)+" "
    else:
        return ""
    
register.filter('numeroBar',numeroBar)
register.filter('numeroNoBar',numeroNoBar)
