from django import template

register = template.Library()


@register.filter
def intcomma(value):
    return "{:,}".format(value)
