from django import template

register = template.Library()

@register.filter
def contains(value, arg):
    """Проверяет, содержится ли подстрока arg в строке value"""
    if isinstance(value, str) and isinstance(arg, str):
        return arg in value
    return False
