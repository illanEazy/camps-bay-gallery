from django.conf import settings


# FILE: gallery/context_processors.py - Updated to handle sold items

def cart_context(request):
    """Context processor to add cart count to all templates - updated to filter out sold items"""
    cart = request.session.get('cart', {})
    
    # Filter out sold items from cart count
    cart_count = 0
    cart_items = []
    
    for artwork_id, item_data in cart.items():
        try:
            # Check if artwork exists and is not sold
            artwork = Artwork.objects.get(id=artwork_id, is_active=True)
            if not artwork.sold:
                cart_count += 1
                cart_items.append({
                    'artwork': {
                        'id': artwork.id,
                        'title': artwork.title,
                        'price': float(artwork.price) if artwork.price else 0,
                    }
                })
        except Artwork.DoesNotExist:
            # Remove invalid artwork from cart
            if str(artwork_id) in cart:
                del cart[str(artwork_id)]
                request.session['cart'] = cart
    
    # Update cart count in session
    request.session['cart_count'] = cart_count
    
    # Clear quick purchase from session if it's not being used
    if request.session.get('quick_purchase') and not request.path.startswith('/checkout'):
        request.session.pop('quick_purchase', None)
        request.session.pop('guest_checkout_item', None)
    
    return {
        'cart_count': cart_count,
        'has_cart_items': cart_count > 0,
        'cart_items_preview': cart_items[:3]  # First 3 items for preview
    }

  # FILE: gallery/context_processors.py - Updated to handle sold items

