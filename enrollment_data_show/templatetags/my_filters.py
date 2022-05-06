from django import template
from datetime import date

register = template.Library()


@register.filter(name='year')
def year(random_parameter):
    return range(date.today().year, 1900, -1)
