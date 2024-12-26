from django import template

register = template.Library()

@register.filter
def sum_total(cart_items):
    """
    Считает общую стоимость корзины.
    """
    return sum(item.total_price for item in cart_items)