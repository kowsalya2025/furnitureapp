from urllib.parse import quote

from django import template

register = template.Library()

def _visible_placeholder(label='No Image'):
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='220' height='160'>"
        "<rect width='100%' height='100%' fill='#f4f4f4'/>"
        "<rect x='14' y='14' width='192' height='132' rx='10' fill='#ffffff' stroke='#dedede'/>"
        "<text x='110' y='88' text-anchor='middle' font-family='Arial, sans-serif' "
        "font-size='16' fill='#999999'>{}</text>"
        "</svg>"
    ).format(label)
    return f"data:image/svg+xml;utf8,{quote(svg)}"


@register.simple_tag(takes_context=True)
def product_image_src(context, product):
    """
    Return a URL that resolves to the product image, with fallbacks when the
    file is missing or MEDIA is not reachable.
    """
    request = context.get('request')
    if not product or not getattr(product, 'image', None) or not getattr(product.image, 'name', None):
        return _visible_placeholder()
    try:
        if not product.image.storage.exists(product.image.name):
            return _visible_placeholder()
        # Ignore tiny 1x1 seed placeholders that render as invisible.
        if product.image.storage.size(product.image.name) < 300:
            return _visible_placeholder(product.name[:16] or 'Product')
    except Exception:
        return _visible_placeholder()
    url = product.image.url
    if request and url.startswith('/'):
        return f'{request.scheme}://{request.get_host()}{url}'
    return url


