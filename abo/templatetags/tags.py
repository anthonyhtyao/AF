from django import template

register = template.Library()

@register.filter
def replace_linebr(value):
    """Replaces all values of line break from the given string with a line space."""
    return value.replace("<br>", ' ')

register.filter('replace_linebr',replace_linebr)
