from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Basic Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('artists/', views.artists, name='artists'),
    path('artists/<int:artist_id>/', views.artist_detail, name='artist_detail'),
    path('artworks/', views.artworks, name='artworks'),
    path('contact/', views.contact, name='contact'),

    # Artwork Detail URLs
    path('artworks/<int:artwork_id>/', views.artwork_detail, name='artwork_detail'),
    path('artworks/<int:artwork_id>/purchase/', views.artwork_purchase, name='artwork_purchase'),
    # REMOVED: schedule_viewing URL
    path('artworks/<int:artwork_id>/inquire/', views.artwork_inquire, name='artwork_inquire'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password-verify/', views.reset_password_verify_view, name='reset_password_verify'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    path('profile/', views.profile_view, name='profile'),

    # Cart and Checkout URLs
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('add-to-cart/<int:artwork_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:artwork_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:artwork_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),

    # Add to urlpatterns
    path('order-confirmation/<str:order_ref>/', views.order_confirmation, name='order_confirmation'),
    
    # ADMIN DASHBOARD URL
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    
    # ARTIST MANAGEMENT URLs
    path('dashboard/artists/add/', views.add_artist_view, name='add_artist'),
    path('dashboard/artists/', views.view_artists_view, name='view_artists'),
    path('dashboard/artists/<int:artist_id>/edit/', views.edit_artist_view, name='edit_artist'),
    path('dashboard/artists/<int:artist_id>/delete/', views.delete_artist_view, name='delete_artist'),
    path('dashboard/manage-artists/', views.manage_artists_view, name='manage_artists'),

    # ARTWORK MANAGEMENT URLs
    path('dashboard/artworks/add/', views.add_artwork_view, name='add_artwork'),
    path('dashboard/artworks/', views.view_artworks_view, name='view_artworks'),
    path('dashboard/artworks/<int:artwork_id>/edit/', views.edit_artwork_view, name='edit_artwork'),
    path('dashboard/artworks/<int:artwork_id>/delete/', views.delete_artwork_view, name='delete_artwork'),

    path('dashboard/artworks/<int:artwork_id>/mark-sold/', views.mark_as_sold, name='mark_as_sold'),
    path('dashboard/artworks/<int:artwork_id>/mark-available/', views.mark_as_available, name='mark_as_available'),
    
    # Placeholder URLs
    path('dashboard/manage-artworks/', views.manage_artworks_view, name='manage_artworks'),
    path('dashboard/analytics/', views.analytics_view, name='analytics'),
    path('orders/', views.view_orders_view, name='view_orders'),
    
    # Social Auth URLs
    path('accounts/', include('allauth.urls')),
]

