from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ... existing URLs ...
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('artists/', views.artists, name='artists'),
    path('artists/<int:artist_id>/', views.artist_detail, name='artist_detail'),
    path('artworks/', views.artworks, name='artworks'),
    path('contact/', views.contact, name='contact'),


        # Artwork Detail URLs (Placeholder for now)
    path('artworks/<int:artwork_id>/', views.artwork_detail, name='artwork_detail'),
    path('artworks/<int:artwork_id>/purchase/', views.artwork_purchase, name='artwork_purchase'),
    path('artworks/<int:artwork_id>/schedule/', views.schedule_viewing, name='schedule_viewing'),
    path('artworks/<int:artwork_id>/inquire/', views.artwork_inquire, name='artwork_inquire'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # New authentication URLs
    path('verify-email/', views.verify_email_view, name='verify_email'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password-verify/', views.reset_password_verify_view, name='reset_password_verify'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    path('profile/', views.profile_view, name='profile'),
    
    # ADMIN DASHBOARD URL
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    
    # FIXED: Added 'dashboard/' prefix to avoid conflicts
    path('dashboard/artists/add/', views.add_artist_view, name='add_artist'),
    path('dashboard/artists/', views.view_artists_view, name='view_artists'),
    path('dashboard/artists/<int:artist_id>/edit/', views.edit_artist_view, name='edit_artist'),
    path('dashboard/artists/<int:artist_id>/delete/', views.delete_artist_view, name='delete_artist'),
    path('dashboard/manage-artists/', views.manage_artists_view, name='manage_artists'),
    
    # Social Auth URLs
    path('accounts/', include('allauth.urls')),
]
