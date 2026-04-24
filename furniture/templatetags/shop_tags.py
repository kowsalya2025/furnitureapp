from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def product_image_src(context, product):
    """
    Return a URL that resolves to the product image, with fallbacks when the
    file is missing. Returns deterministically beautiful static product images 
    (pro1.png - pro9.png) instead of empty SVG placeholders to maintain 
    premium aesthetic continuity.
    """
    if product and getattr(product, 'image', None) and getattr(product.image, 'name', None):
        try:
            if product.image.storage.exists(product.image.name) and product.image.storage.size(product.image.name) > 300:
                return product.image.url
        except Exception:
            pass
            
    # Deterministic beautiful fallback based on product ID
    if product and getattr(product, 'id', None):
        fallback_num = (product.id % 9) + 1
        # Quick guard clause for exact filename matching
        if fallback_num == 0:
            fallback_num = 1
    else:
        fallback_num = 1
        
    return f'/static/images/pro{fallback_num}.png'
