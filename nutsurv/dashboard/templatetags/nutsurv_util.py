from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def as_inverse_percentage_of(part, whole):
    try:
        return '{0:.2%}'.format(1.0 - ((float(part) / float(whole))))
    except (ValueError, ZeroDivisionError):
        return ""

@register.filter
def as_percentage_of(part, whole):
    try:
        return '{0:.2%}'.format((float(part) / float(whole)))
    except (ValueError, ZeroDivisionError):
        return ""


@register.filter
@stringfilter
def underscores_to_spaces(value):
    return value.replace('_', ' ')
