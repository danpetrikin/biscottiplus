# Some custom filters for dictionary lookup.
from django.template.defaultfilters import register

from django.conf import settings
from django.template import defaultfilters

@register.filter(name='multiplymoney')
def multiplymoney(first,second):
    return '{:20,.2f}'.format(float(first) * float(second))