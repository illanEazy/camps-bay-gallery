from django.conf import settings


def cart_context(request):
    """Context processor to add cart count to all templates"""
    cart = request.session.get('cart', {})
    cart_count = len(cart)
    
    # Clear quick purchase from session if it's not being used
    # Only show quick purchase count if we're actively in checkout
    if request.session.get('quick_purchase') and not request.path.startswith('/checkout'):
        # Clear quick purchase if not in checkout
        request.session.pop('quick_purchase', None)
        request.session.pop('guest_checkout_item', None)
    
    return {
        'cart_count': cart_count,
        'has_cart_items': cart_count > 0
    }