from django import template

register = template.Library()


@register.filter
def replace_underscore(string):
    if string:
        return string.replace('_', ' ')
    return ""


@register.filter
def filler_words_list(strlist):
    if not strlist:
        return "No filler found."
    return ",".join(strlist)


@register.filter
def replace_double_dot(string):
    return string.replace('..', '.')
