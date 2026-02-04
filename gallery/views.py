from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
from django.views.decorators.http import require_POST
from datetime import timedelta
import json

# Add these form imports
from .forms import (
    CustomLoginForm, CustomSignupForm, OTPVerificationForm,
    CustomForgotPasswordForm, CustomResetPasswordForm, 
    UserProfileForm, ArtworkForm, CheckoutForm
)
from .models import User, OTP, UserProfile, Artist, Artwork
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import ArtistForm
# Add this import at the top of views.py with other imports
import random


# ============================================================================
# BASIC VIEWS
# ============================================================================

def home(request):
    """Home page view - updated to include sold artworks and show images correctly"""
    # Get featured artworks (including sold ones)
    featured_artworks_db = Artwork.objects.filter(is_active=True).select_related('artist').order_by('-created_at')[:6]
    
    # Format featured artworks as dictionaries (consistent with artworks page)
    featured_artworks = []
    for artwork in featured_artworks_db:
        featured_artworks.append({
            'id': artwork.id,
            'title': artwork.title,
            'artist': artwork.artist.full_name,
            'artist_id': artwork.artist.id,
            'image': artwork.primary_image,  # This now uses the fixed property
            'year': artwork.year,
            'medium': artwork.medium,
            'availability': artwork.availability,
            'sold': artwork.sold,
            'show_price': artwork.show_price,
            'price': float(artwork.price) if artwork.price else None,
            'discounted_price': float(artwork.discounted_price) if artwork.discounted_price else None,
            'dimensions': artwork.dimensions,
            'allow_purchase': artwork.allow_purchase,
            'allow_inquiry': artwork.allow_inquiry,
            'allow_schedule_viewing': artwork.allow_schedule_viewing
        })
    
    # Get active artists for carousel
    artists = Artist.objects.filter(is_active=True).order_by('first_name', 'last_name')[:10]
    
    context = {
        'featured_artworks': featured_artworks,
        'artists': artists,
        'page_title': 'Home',
        'page_subtitle': 'Contemporary Art Gallery in Camps Bay'
    }
    
    return render(request, 'gallery/index.html', context)


def about(request):
    """Render the about page"""
    return render(request, 'gallery/about.html')


def artists(request):
    """Render the artists overview page"""
    # Get all active artists from database
    artists = Artist.objects.filter(is_active=True).order_by('first_name', 'last_name')
    context = {'artists': artists}
    return render(request, 'gallery/artists.html', context)


# Update the artist_detail function:
def artist_detail(request, artist_id):
    """Render individual artist detail page"""
    # Get artist from database
    artist = get_object_or_404(Artist, id=artist_id, is_active=True)
    
    # Get artist's artworks from database
    artist_artworks_db = Artwork.objects.filter(artist=artist, is_active=True)
    
    # Format for template
    artist_artworks = []
    for artwork in artist_artworks_db:
        artist_artworks.append({
            'id': artwork.id,
            'title': artwork.title,
            'artist': artwork.artist.full_name,
            'artist_id': artwork.artist.id,
            'image': artwork.primary_image,
            'year': artwork.year,
            'medium': artwork.medium,
            'availability': artwork.availability,
            'sold': artwork.sold,
            'show_price': artwork.show_price,
            'price': float(artwork.price) if artwork.price else None,
            'discounted_price': float(artwork.discounted_price) if artwork.discounted_price else None,
            'dimensions': artwork.dimensions,
            'allow_purchase': artwork.allow_purchase,
            'allow_inquiry': artwork.allow_inquiry,
            'allow_schedule_viewing': artwork.allow_schedule_viewing
        })
    
    context = {
        'artist': artist,
        'artist_artworks': artist_artworks
    }
    return render(request, 'gallery/artist_detail.html', context)

# FILE: gallery/views.py - Update artworks view with working filters
def artworks(request):
    """Display all artworks with working filters and sorting"""
    # Get filter and sort parameters
    search_query = request.GET.get('q', '')
    artist_filter = request.GET.get('artist', '')
    medium_filter = request.GET.get('medium', '')
    sort_by = request.GET.get('sort', 'newest')
    
    # Start with all active artworks
    artworks_list = Artwork.objects.filter(is_active=True).select_related('artist')
    
    # Apply search filter
    if search_query:
        artworks_list = artworks_list.filter(
            Q(title__icontains=search_query) |
            Q(artist__first_name__icontains=search_query) |
            Q(artist__last_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(medium__icontains=search_query)
        )
    
    # Apply artist filter
    if artist_filter and artist_filter != 'all':
        artworks_list = artworks_list.filter(artist__id=artist_filter)
    
    # Apply medium filter
    if medium_filter:
        artworks_list = artworks_list.filter(medium__icontains=medium_filter)
    
    # Apply sorting
    if sort_by == 'newest':
        artworks_list = artworks_list.order_by('-created_at')
    elif sort_by == 'oldest':
        artworks_list = artworks_list.order_by('created_at')
    elif sort_by == 'title_asc':
        artworks_list = artworks_list.order_by('title')
    elif sort_by == 'title_desc':
        artworks_list = artworks_list.order_by('-title')
    elif sort_by == 'price_low':
        artworks_list = artworks_list.order_by('price')
    elif sort_by == 'price_high':
        artworks_list = artworks_list.order_by('-price')
    else:
        artworks_list = artworks_list.order_by('-created_at')
    
    # Get total count before pagination
    total_artworks = artworks_list.count()
    
    # Pagination
    paginator = Paginator(artworks_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all artists for filter dropdown
    artists = Artist.objects.filter(is_active=True).order_by('first_name', 'last_name')
    
    # Prepare artworks data for template
    artworks_data = []
    for artwork in page_obj:
        artworks_data.append({
            'id': artwork.id,
            'title': artwork.title,
            'artist': artwork.artist.full_name,
            'artist_id': artwork.artist.id,
            'image': artwork.primary_image,  # This now uses the fixed property
            'year': artwork.year,
            'medium': artwork.medium,
            'availability': artwork.availability,
            'sold': artwork.sold,
            'show_price': artwork.show_price,
            'price': float(artwork.price) if artwork.price else None,
            'discounted_price': float(artwork.discounted_price) if artwork.discounted_price else None,
            'dimensions': artwork.dimensions,
            'allow_purchase': artwork.allow_purchase,
            'allow_inquiry': artwork.allow_inquiry,
            'allow_schedule_viewing': artwork.allow_schedule_viewing
        })
    
    context = {
        'artworks': artworks_data,
        'page_obj': page_obj,
        'total_artworks': total_artworks,
        'search_query': search_query,
        'current_artist': artist_filter,
        'current_sort': sort_by,
        'artists': artists,
        'is_paginated': paginator.num_pages > 1,
        'page_title': 'Artworks',
        'page_subtitle': 'Browse our collection of exceptional artworks'
    }
    
    return render(request, 'gallery/artworks.html', context)

def contact(request):
    """Render the contact page"""
    return render(request, 'gallery/contact.html')

def google_login_redirect(request):
    """Redirect to Google OAuth login via allauth"""
    return redirect('account_login')



# ============================================================================
# ARTWORK DETAIL VIEWS - ONLY ONE SET OF FUNCTIONS
# ============================================================================
def artwork_detail(request, artwork_id):
    """Render artwork detail page from database"""
    try:
        # Get artwork from database
        artwork = Artwork.objects.get(id=artwork_id, is_active=True)
        
        context = {
            'artwork': {
                'id': artwork.id,
                'title': artwork.title,
                'artist': artwork.artist.full_name,
                'artist_id': artwork.artist.id,
                'description': artwork.description,
                'medium': artwork.medium,
                'dimensions': artwork.dimensions,
                'year': artwork.year,
                'image': artwork.primary_image,
                'availability': artwork.availability,
                'sold': artwork.sold,
                'show_price': artwork.show_price,
                'price': float(artwork.price) if artwork.price else None,
                'discounted_price': float(artwork.discounted_price) if artwork.discounted_price else None,
                'allow_purchase': artwork.allow_purchase,
                'allow_inquiry': artwork.allow_inquiry,
                'allow_schedule_viewing': artwork.allow_schedule_viewing
            },
            'show_inquiry_modal': (artwork.availability == 'on_request'),
            'user': request.user,
        }
        return render(request, 'gallery/artwork_detail.html', context)
        
    except Artwork.DoesNotExist:
        messages.error(request, 'Artwork not found.')
        return redirect('artworks')



def artwork_purchase(request, artwork_id):
    """Handle artwork purchase - redirect to detail page"""
    return redirect('artwork_detail', artwork_id=artwork_id)


def artwork_inquire(request, artwork_id):
    """Handle artwork inquiry form submission"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Find artwork
        artwork = None
        for a in GLOBAL_ARTWORKS_DATA:
            if a['id'] == artwork_id:
                artwork = a
                break
        
        if artwork and name and email and message:
            print(f"Inquiry received for {artwork['title']}")
            print(f"From: {name} ({email})")
            print(f"Message: {message[:100]}...")
            
            messages.success(request, 'Your inquiry has been sent! We\'ll get back to you soon.')
            return redirect('artwork_detail', artwork_id=artwork_id)
        else:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('artwork_detail', artwork_id=artwork_id)
    
    # GET request - just redirect to detail page
    return redirect('artwork_detail', artwork_id=artwork_id)

# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

def login_view(request):
    """Simple login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomLoginForm(request.POST, request=request)
        if form.is_valid():
            user = form.user_cache
            
            if user is not None:
                if not user.is_email_verified:
                    messages.error(request, 'Please verify your email address first.')
                    return render(request, 'gallery/login.html', {'form': form})
                
                login(request, user)
                messages.success(request, 'Logged in successfully!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomLoginForm(request=request)
    
    context = {
        'form': form,
        'auth_title': 'Login',
        'auth_subtitle': 'Welcome back to Camps Bay Gallery'
    }
    return render(request, 'gallery/login.html', context)

def signup_view(request):
    """Simple signup view with direct email sending"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_email_verified = False
                user.save()
                
                otp_code = OTP.generate_otp()
                expires_at = timezone.now() + timedelta(minutes=15)
                
                OTP.objects.create(
                    user=user,
                    otp_code=otp_code,
                    otp_type='email_verification',
                    expires_at=expires_at
                )
                
                request.session['pending_user_id'] = user.id
                request.session['pending_user_email'] = user.email
                
                verification_url = request.build_absolute_uri(reverse('verify_email'))
                
                html_message = render_to_string('gallery/emails/verify_email_email.html', {
                    'user': user,
                    'otp_code': otp_code,
                    'verification_url': verification_url,
                })
                
                plain_message = f"""
                Hello {user.first_name},
                
                Your verification code is: {otp_code}
                
                Enter this code to activate your account.
                Code expires in 15 minutes.
                
                Camps Bay Gallery Team
                """
                
                send_mail(
                    subject='Verify Your Email - Camps Bay Art Gallery',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                print(f"✅ Verification email sent to {user.email}")
                print(f"   OTP: {otp_code}")
                
                messages.success(request, 'Verification email sent! Please check your inbox.')
                return redirect('verify_email')
                
            except Exception as e:
                print(f"❌ Signup error: {e}")
                messages.error(request, 'Registration failed. Please try again.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomSignupForm()
    
    return render(request, 'gallery/signup.html', {'form': form})

def verify_email_view(request):
    """Handle email verification with OTP"""
    user_id = request.session.get('pending_user_id')
    
    if not user_id:
        messages.error(request, 'No pending verification found. Please sign up again.')
        return redirect('signup')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = OTPVerificationForm(user=user, otp_type='email_verification', data=request.POST)
        if form.is_valid():
            otp_instance = form.otp_instance
            otp_instance.mark_used()
            
            user.is_email_verified = True
            user.save()
            
            del request.session['pending_user_id']
            del request.session['pending_user_email']
            
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            messages.success(request, 'Email verified successfully! Welcome to Camps Bay Gallery.')
            return redirect('home')
    else:
        form = OTPVerificationForm()
    
    context = {
        'form': form,
        'email': request.session.get('pending_user_email', ''),
    }
    return render(request, 'gallery/verify_email.html', context)

def forgot_password_view(request):
    """Simple forgot password view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomForgotPasswordForm(request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data.get('email')
                user = User.objects.get(email=email)
                
                if not user.is_email_verified:
                    messages.error(request, 'Please verify your email address first.')
                    return render(request, 'gallery/forgot_password.html', {'form': form})
                
                otp_code = OTP.generate_otp()
                expires_at = timezone.now() + timedelta(minutes=15)
                
                OTP.objects.filter(user=user, otp_type='password_reset').delete()
                
                OTP.objects.create(
                    user=user,
                    otp_code=otp_code,
                    otp_type='password_reset',
                    expires_at=expires_at
                )
                
                request.session['reset_user_id'] = user.id
                
                reset_url = request.build_absolute_uri(reverse('reset_password_verify'))
                
                html_message = render_to_string('gallery/emails/password_reset.html', {
                    'user': user,
                    'otp_code': otp_code,
                    'reset_url': reset_url,
                })
                
                plain_message = f"""
                Hello {user.first_name},
                
                Your password reset code is: {otp_code}
                
                Enter this code to reset your password.
                Code expires in 15 minutes.
                
                Camps Bay Gallery Team
                """
                
                send_mail(
                    subject='Password Reset - Camps Bay Art Gallery',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                print(f"✅ Password reset email sent to {user.email}")
                print(f"   OTP: {otp_code}")
                
                messages.success(request, 'Password reset email sent! Please check your inbox.')
                return redirect('reset_password_verify')
                
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
            except Exception as e:
                print(f"❌ Forgot password error: {e}")
                messages.error(request, 'Failed to send reset email. Please try again.')
    else:
        form = CustomForgotPasswordForm()
    
    context = {
        'form': form,
        'auth_title': 'Reset Password',
        'auth_subtitle': 'Enter your email to reset your password'
    }
    return render(request, 'gallery/forgot_password.html', context)

def reset_password_verify_view(request):
    """Verify OTP for password reset"""
    user_id = request.session.get('reset_user_id')
    
    if not user_id:
        messages.error(request, 'No password reset request found.')
        return redirect('forgot_password')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = OTPVerificationForm(user=user, otp_type='password_reset', data=request.POST)
        if form.is_valid():
            otp_instance = form.otp_instance
            otp_instance.mark_used()
            
            request.session['reset_verified'] = True
            
            messages.success(request, 'OTP verified. You can now reset your password.')
            return redirect('reset_password')
    else:
        form = OTPVerificationForm()
    
    context = {
        'form': form,
        'auth_title': 'Verify OTP',
        'auth_subtitle': 'Enter the 6-digit code sent to your email'
    }
    return render(request, 'gallery/reset_password_verify.html', context)

def reset_password_view(request):
    """Reset password after OTP verification"""
    if not request.session.get('reset_verified'):
        messages.error(request, 'Please verify OTP first.')
        return redirect('forgot_password')
    
    user_id = request.session.get('reset_user_id')
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = CustomResetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            request.session.pop('reset_verified', None)
            request.session.pop('reset_user_id', None)
            
            messages.success(request, 'Password reset successfully. You can now login.')
            return redirect('login')
    else:
        form = CustomResetPasswordForm(user)
    
    context = {
        'form': form,
        'auth_title': 'Set New Password',
        'auth_subtitle': 'Create a new password for your account'
    }
    return render(request, 'gallery/reset_password.html', context)

@login_required
def profile_view(request):
    """User profile page"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)
    
    context = {
        'profile': user_profile,
        'form': form,
        'user': request.user
    }
    return render(request, 'gallery/profile.html', context)

def logout_view(request):
    """Simple logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@csrf_exempt
@require_POST
def resend_otp_view(request):
    """Resend OTP - Simple JSON response"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        otp_type = data.get('otp_type')
        
        user = get_object_or_404(User, id=user_id)
        
        OTP.objects.filter(user=user, otp_type=otp_type, is_used=False).delete()
        
        otp_code = OTP.generate_otp()
        expires_at = timezone.now() + timedelta(minutes=15)
        
        OTP.objects.create(
            user=user,
            otp_code=otp_code,
            otp_type=otp_type,
            expires_at=expires_at
        )
        
        if otp_type == 'email_verification':
            subject = 'New Verification Code - Camps Bay Gallery'
            verification_url = request.build_absolute_uri(reverse('verify_email'))
            
            html_message = render_to_string('gallery/emails/verify_email_email.html', {
                'user': user,
                'otp_code': otp_code,
                'verification_url': verification_url,
            })
        else:
            subject = 'New Password Reset Code - Camps Bay Gallery'
            reset_url = request.build_absolute_uri(reverse('reset_password_verify'))
            
            html_message = render_to_string('gallery/emails/password_reset.html', {
                'user': user,
                'otp_code': otp_code,
                'reset_url': reset_url,
            })
        
        plain_message = f"""
        Your new code is: {otp_code}
        
        Enter this code to continue.
        Code expires in 15 minutes.
        
        Camps Bay Gallery Team
        """
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        print(f"✅ {otp_type} email resent to {user.email}")
        
        return JsonResponse({'success': True, 'message': 'New code sent to your email.'})
    except Exception as e:
        print(f"❌ Resend OTP error: {e}")
        return JsonResponse({'success': False, 'error': 'Failed to resend code.'})

# ============================================================================
# ADMIN DASHBOARD VIEW
# ============================================================================

@login_required
def admin_dashboard_view(request):
    """Admin dashboard view - accessible only to owners"""
    if not request.user.is_owner:
        messages.error(request, 'Access denied. Admin dashboard is for owners only.')
        return redirect('home')
    
    context = {
        'user': request.user,
        'dashboard_title': 'Admin Dashboard',
        'dashboard_subtitle': 'Manage your gallery content and view analytics'
    }
    return render(request, 'gallery/admin_dashboard.html', context)

# ============================================================================
# ARTIST MANAGEMENT VIEWS
# ============================================================================

def is_owner(user):
    return user.is_authenticated and user.is_owner

@login_required
@user_passes_test(lambda u: u.is_owner)
def add_artist_view(request):
    """Add a new artist to the database"""
    if request.method == 'POST':
        form = ArtistForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                artist = form.save()
                messages.success(
                    request, 
                    f'Artist "{artist.first_name} {artist.last_name if artist.last_name else ""}" added successfully!'
                )
                return redirect('admin_dashboard')  # Redirect to dashboard after adding
            except Exception as e:
                messages.error(request, f'Error saving artist: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ArtistForm()
    
    context = {
        'form': form,
        'page_title': 'Add Artist',
        'page_subtitle': 'Add a new artist to your gallery'
    }
    return render(request, 'gallery/add_artist.html', context)


@login_required
@user_passes_test(is_owner)
def view_artists_view(request):
    """View all artists with search and pagination"""
    search_query = request.GET.get('q', '')
    
    artists = Artist.objects.all().order_by('first_name', 'last_name')
    
    if search_query:
        artists = artists.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(specialty__icontains=search_query) |
            Q(bio__icontains=search_query)
        )
    
    paginator = Paginator(artists, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'artists': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'is_paginated': paginator.num_pages > 1,
        'page_title': 'View Artists',
        'page_subtitle': 'Manage artists in your gallery'
    }
    return render(request, 'gallery/view_artists.html', context)

@login_required
@user_passes_test(is_owner)
def edit_artist_view(request, artist_id):
    """Edit an existing artist"""
    try:
        artist = Artist.objects.get(id=artist_id)
    except Artist.DoesNotExist:
        messages.error(request, 'Artist not found.')
        return redirect('view_artists')
    
    if request.method == 'POST':
        form = ArtistForm(request.POST, request.FILES, instance=artist)
        
        if request.POST.get('remove_current_image') == '1':
            if artist.profile_picture:
                artist.profile_picture.delete(save=False)
                artist.profile_picture = None
        
        if form.is_valid():
            artist = form.save()
            messages.success(request, f'Artist "{artist.first_name} {artist.last_name}" updated successfully!')
            return redirect('view_artists')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ArtistForm(instance=artist)
    
    context = {
        'form': form,
        'artist': artist,
        'page_title': 'Edit Artist',
        'page_subtitle': f'Edit {artist.first_name} {artist.last_name}'
    }
    return render(request, 'gallery/edit_artist.html', context)

@login_required
@user_passes_test(is_owner)
def delete_artist_view(request, artist_id):
    """Delete an artist"""
    try:
        artist = Artist.objects.get(id=artist_id)
        artist_name = f"{artist.first_name} {artist.last_name}"
        
        artist.delete()
        
        messages.success(request, f'Artist "{artist_name}" deleted successfully!')
        
    except Artist.DoesNotExist:
        messages.error(request, 'Artist not found.')
    
    return redirect('view_artists')

@login_required
def manage_artists_view(request):
    """Redirect to view artists page"""
    if not request.user.is_owner:
        messages.error(request, 'Access denied. Admin features are for owners only.')
        return redirect('home')
    
    return redirect('view_artists')

# ============================================================================
# ARtWOKR MANAGEMENT VIEWS (Placeholder)
# ============================================================================
# Replace the placeholder artwork views with these actual implementations

@login_required
@user_passes_test(is_owner)
def add_artwork_view(request):
    """Add a new artwork to the database"""
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save the artwork
                artwork = form.save(commit=False)
                artwork.created_by = request.user
                artwork.save()
                
                messages.success(
                    request, 
                    f'Artwork "{artwork.title}" added successfully!'
                )
                return redirect('view_artworks')
            except Exception as e:
                messages.error(request, f'Error saving artwork: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ArtworkForm()
    
    # Get all active artists for the template
    artists = Artist.objects.filter(is_active=True).order_by('first_name', 'last_name')
    
    context = {
        'form': form,
        'artists': artists,
        'page_title': 'Add Artwork',
        'page_subtitle': 'Add a new artwork to your gallery collection'
    }
    return render(request, 'gallery/add_artwork.html', context)

@login_required
@user_passes_test(is_owner)
def view_artworks_view(request):
    """View all artworks with search and pagination"""
    search_query = request.GET.get('q', '')
    
    # Get all artworks from database
    artworks = Artwork.objects.all().select_related('artist').order_by('-created_at')
    
    if search_query:
        artworks = artworks.filter(
            Q(title__icontains=search_query) |
            Q(artist__first_name__icontains=search_query) |
            Q(artist__last_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(medium__icontains=search_query)
        )
    
    paginator = Paginator(artworks, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'artworks': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'is_paginated': paginator.num_pages > 1,
        'page_title': 'View Artworks',
        'page_subtitle': 'Manage artworks in your gallery'
    }
    return render(request, 'gallery/view_artworks.html', context)


@login_required
@user_passes_test(is_owner)
def edit_artwork_view(request, artwork_id):
    """Edit an existing artwork"""
    try:
        artwork = Artwork.objects.get(id=artwork_id)
    except Artwork.DoesNotExist:
        messages.error(request, 'Artwork not found.')
        return redirect('view_artworks')
    
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES, instance=artwork)
        
        if request.POST.get('remove_current_image') == '1':
            if artwork.image:
                artwork.image.delete(save=False)
                artwork.image = None
        
        if form.is_valid():
            artwork = form.save()
            messages.success(request, f'Artwork "{artwork.title}" updated successfully!')
            return redirect('view_artworks')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ArtworkForm(instance=artwork)
    
    # Get all active artists for the template
    artists = Artist.objects.filter(is_active=True).order_by('first_name', 'last_name')
    
    context = {
        'form': form,
        'artists': artists,
        'artwork': artwork,
        'page_title': 'Edit Artwork',
        'page_subtitle': f'Edit {artwork.title}'
    }
    return render(request, 'gallery/edit_artwork.html', context)

@login_required
@user_passes_test(is_owner)
def delete_artwork_view(request, artwork_id):
    """Delete an artwork"""
    try:
        artwork = Artwork.objects.get(id=artwork_id)
        artwork_title = artwork.title
        
        artwork.delete()
        
        messages.success(request, f'Artwork "{artwork_title}" deleted successfully!')
        
    except Artwork.DoesNotExist:
        messages.error(request, 'Artwork not found.')
    
    return redirect('view_artworks')


# ============================================================================
# PLACEHOLDER VIEWS
# ============================================================================

@login_required
def manage_artworks_view(request):
    """Placeholder view for managing artworks - FUTURE FEATURE"""
    if not request.user.is_owner:
        messages.error(request, 'Access denied. Admin features are for owners only.')
        return redirect('home')
    
    messages.info(request, 'Manage Artworks feature is coming soon!')
    return redirect('admin_dashboard')

@login_required
def analytics_view(request):
    """Placeholder view for analytics dashboard - FUTURE FEATURE"""
    if not request.user.is_owner:
        messages.error(request, 'Access denied. Admin features are for owners only.')
        return redirect('home')
    
    messages.info(request, 'Analytics Dashboard is coming soon!')
    return redirect('admin_dashboard')

@login_required
def view_orders_view(request):
    """View orders for customers"""
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to view your orders.')
        return redirect('login')
    
    messages.info(request, 'Order history feature is coming soon!')
    
    if request.user.is_owner:
        return redirect('admin_dashboard')
    else:
        return redirect('profile')

# ============================================================================
# UPDATED CHECKOUT VIEWS
# ============================================================================
# FILE: gallery/views.py - Update cart_view function

def add_to_cart(request, artwork_id):
    """Add artwork to cart - prevent adding sold items"""
    if request.method == 'POST':
        try:
            # Get the artwork from database
            artwork = Artwork.objects.get(id=artwork_id)
            
            # Check if artwork is sold
            if artwork.sold:
                messages.error(request, f'Sorry, "{artwork.title}" has been sold and is no longer available.')
                return redirect('artwork_detail', artwork_id=artwork_id)
            
            # Check if artwork is active
            if not artwork.is_active:
                messages.error(request, f'Sorry, "{artwork.title}" is currently not available.')
                return redirect('artwork_detail', artwork_id=artwork_id)
            
            # Check if it's a quick purchase
            action = request.POST.get('action', 'add_to_cart')
            
            if action == 'quick_purchase':
                # Set quick purchase in session
                request.session['quick_purchase'] = artwork_id
                messages.success(request, f'Proceeding to quick purchase for "{artwork.title}".')
                
                # If user is not logged in, store artwork in session for guest checkout
                if not request.user.is_authenticated:
                    request.session['guest_checkout_item'] = {
                        'id': artwork.id,
                        'title': artwork.title,
                        'artist': artwork.artist.full_name,
                        'price': float(artwork.price) if artwork.price else 0,
                        'image': artwork.primary_image,
                        'medium': artwork.medium,
                        'dimensions': artwork.dimensions
                    }
                
                return redirect('checkout')
            else:
                # Normal add to cart
                cart = request.session.get('cart', {})
                
                if str(artwork_id) not in cart:
                    cart[str(artwork_id)] = {
                        'quantity': 1,
                        'added_at': timezone.now().isoformat(),
                        'title': artwork.title,
                        'artist': artwork.artist.full_name,
                        'price': float(artwork.price) if artwork.price else 0,
                        'image': artwork.primary_image
                    }
                    request.session['cart'] = cart
                    messages.success(request, f'"{artwork.title}" added to cart.')
                    
                    # Update cart count (only for normal add to cart)
                    cart_count = len(cart)
                    request.session['cart_count'] = cart_count
                else:
                    messages.info(request, f'"{artwork.title}" is already in your cart.')
            
            # Check where to redirect
            redirect_to = request.POST.get('redirect_to', 'cart')
            
            if redirect_to == 'checkout':
                # For normal checkout from cart, clear quick purchase
                request.session.pop('quick_purchase', None)
                request.session.pop('guest_checkout_item', None)
                return redirect('checkout')
            else:
                return redirect('cart')
            
        except Artwork.DoesNotExist:
            messages.error(request, 'Artwork not found.')
            return redirect('artworks')
        except Exception as e:
            print(f"❌ Error adding to cart: {e}")
            messages.error(request, 'An error occurred. Please try again.')
            return redirect('artwork_detail', artwork_id=artwork_id)
    
    return redirect('artworks')

def cart_view(request):
    """View shopping cart - updated to handle sold items properly"""
    cart = request.session.get('cart', {})
    
    cart_items = []
    subtotal = 0
    
    for artwork_id, item_data in cart.items():
        try:
            # Get artwork even if it's sold (but still active)
            artwork = Artwork.objects.get(id=artwork_id, is_active=True)
            quantity = item_data.get('quantity', 1)
            
            # Check if artwork is sold - if so, don't include it in cart
            if artwork.sold:
                # Remove sold item from cart
                if str(artwork_id) in cart:
                    del cart[str(artwork_id)]
                    request.session['cart'] = cart
                continue
                
            item_total = float(artwork.price) if artwork.price else 0
            subtotal += item_total
            
            cart_items.append({
                'artwork': {
                    'id': artwork.id,
                    'title': artwork.title,
                    'artist': artwork.artist.full_name,
                    'image': artwork.primary_image,
                    'price': float(artwork.price) if artwork.price else 0,
                    'medium': artwork.medium,
                    'dimensions': artwork.dimensions,
                    'sold': artwork.sold  # Add sold status
                },
                'quantity': quantity,
                'item_total': item_total
            })
        except Artwork.DoesNotExist:
            # Remove invalid item from cart
            if str(artwork_id) in cart:
                del cart[str(artwork_id)]
                request.session['cart'] = cart
            continue
    
    # Calculate totals
    shipping = 500
    tax = subtotal * 0.15
    total = subtotal + shipping + tax
    
    # Update cart count
    cart_count = len(cart_items)
    request.session['cart_count'] = cart_count
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'item_count': cart_count,
        'user': request.user
    }
    
    return render(request, 'gallery/cart.html', context)

# FILE: gallery/views.py - Update cart_view function

def cart_view(request):
    """View shopping cart - updated to handle sold items properly"""
    cart = request.session.get('cart', {})
    
    cart_items = []
    subtotal = 0
    
    for artwork_id, item_data in cart.items():
        try:
            # Get artwork even if it's sold (but still active)
            artwork = Artwork.objects.get(id=artwork_id, is_active=True)
            quantity = item_data.get('quantity', 1)
            
            # Check if artwork is sold - if so, don't include it in cart
            if artwork.sold:
                # Remove sold item from cart
                if str(artwork_id) in cart:
                    del cart[str(artwork_id)]
                    request.session['cart'] = cart
                continue
                
            item_total = float(artwork.price) if artwork.price else 0
            subtotal += item_total
            
            cart_items.append({
                'artwork': {
                    'id': artwork.id,
                    'title': artwork.title,
                    'artist': artwork.artist.full_name,
                    'image': artwork.primary_image,
                    'price': float(artwork.price) if artwork.price else 0,
                    'medium': artwork.medium,
                    'dimensions': artwork.dimensions,
                    'sold': artwork.sold  # Add sold status
                },
                'quantity': quantity,
                'item_total': item_total
            })
        except Artwork.DoesNotExist:
            # Remove invalid item from cart
            if str(artwork_id) in cart:
                del cart[str(artwork_id)]
                request.session['cart'] = cart
            continue
    
    # Calculate totals
    shipping = 500
    tax = subtotal * 0.15
    total = subtotal + shipping + tax
    
    # Update cart count
    cart_count = len(cart_items)
    request.session['cart_count'] = cart_count
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'item_count': cart_count,
        'user': request.user
    }
    
    return render(request, 'gallery/cart.html', context)

# FILE: gallery/views.py - Update checkout_view function

def checkout_view(request):
    """Checkout page - updated to handle sold items properly"""
    cart = request.session.get('cart', {})
    quick_purchase_id = request.session.get('quick_purchase')
    guest_checkout_item = request.session.get('guest_checkout_item')
    
    cart_items = []
    subtotal = 0
    
    # Handle quick purchase
    if quick_purchase_id or guest_checkout_item:
        try:
            if quick_purchase_id:
                # Get artwork and check if it's sold
                artwork = Artwork.objects.get(id=quick_purchase_id, is_active=True)
                
                # Check if artwork is sold
                if artwork.sold:
                    messages.error(request, f'Sorry, "{artwork.title}" has been sold and is no longer available.')
                    request.session.pop('quick_purchase', None)
                    request.session.pop('guest_checkout_item', None)
                    return redirect('artworks')
                
                artwork_data = {
                    'id': artwork.id,
                    'title': artwork.title,
                    'artist': artwork.artist.full_name,
                    'price': float(artwork.price) if artwork.price else 0,
                    'image': artwork.primary_image,
                    'medium': artwork.medium,
                    'dimensions': artwork.dimensions
                }
            else:
                # Use guest checkout data
                artwork_data = guest_checkout_item
            
            item_total = float(artwork_data['price']) if artwork_data['price'] else 0
            subtotal = item_total
            
            cart_items.append({
                'artwork': artwork_data,
                'quantity': 1,
                'item_total': item_total
            })
            
        except Artwork.DoesNotExist:
            messages.error(request, 'The selected artwork is no longer available.')
            request.session.pop('quick_purchase', None)
            request.session.pop('guest_checkout_item', None)
            return redirect('artworks')
    else:
        # Normal cart checkout
        if not cart:
            messages.info(request, 'Your cart is empty. Add items before checkout.')
            return redirect('cart')
        
        # Get cart items from cart session data
        for artwork_id, item_data in cart.items():
            try:
                # Get artwork even if it's sold
                artwork = Artwork.objects.get(id=artwork_id, is_active=True)
                
                # Check if artwork is sold
                if artwork.sold:
                    # Remove sold item from cart
                    if str(artwork_id) in cart:
                        del cart[str(artwork_id)]
                        request.session['cart'] = cart
                    messages.warning(request, f'"{artwork.title}" has been sold and was removed from your cart.')
                    continue
                    
                item_total = float(artwork.price) if artwork.price else 0
                subtotal += item_total
                
                cart_items.append({
                    'artwork': {
                        'id': artwork.id,
                        'title': artwork.title,
                        'artist': artwork.artist.full_name,
                        'image': artwork.primary_image,
                        'price': float(artwork.price) if artwork.price else 0,
                    },
                    'quantity': item_data.get('quantity', 1),
                    'item_total': item_total
                })
            except Artwork.DoesNotExist:
                # Remove invalid item from cart
                if str(artwork_id) in cart:
                    del cart[str(artwork_id)]
                    request.session['cart'] = cart
                continue
    
    if not cart_items:
        messages.error(request, 'No items to checkout.')
        return redirect('cart')
    
    # Calculate totals
    shipping = 500
    tax = subtotal * 0.15
    total = subtotal + shipping + tax
    
    # Generate order reference
    order_reference = f"ORD-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'order_reference': order_reference,
        'item_count': len(cart_items),
        'user': request.user,
        'is_quick_purchase': bool(quick_purchase_id or guest_checkout_item)
    }
    
    return render(request, 'gallery/checkout.html', context)

# FILE: gallery/views.py - Update process_checkout function
# FILE: gallery/views.py - COMPLETE process_checkout function
@require_POST
def process_checkout(request):
    """Process the checkout form submission - COMPLETE VERSION"""
    cart = request.session.get('cart', {})
    quick_purchase_id = request.session.get('quick_purchase')
    guest_checkout_item = request.session.get('guest_checkout_item')
    
    # Get form data
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    address = request.POST.get('address', '').strip()
    city = request.POST.get('city', '').strip()
    country = request.POST.get('country', '').strip()
    province = request.POST.get('province', '').strip()
    postal_code = request.POST.get('postal_code', '').strip()
    payment_method = request.POST.get('payment_method', 'card')
    
    # Validate required fields
    required_fields = [first_name, last_name, email, phone, address, city, country, province, postal_code]
    if not all(required_fields):
        messages.error(request, 'Please fill in all required fields.')
        return redirect('checkout')
    
    # Get cart items for processing
    cart_items = []
    subtotal = 0
    artwork_ids = []  # Store artwork IDs to mark as sold
    
    # Handle quick purchase or guest checkout
    if quick_purchase_id or guest_checkout_item:
        try:
            if quick_purchase_id:
                # Get artwork and verify it's not sold
                artwork = Artwork.objects.get(id=quick_purchase_id, is_active=True)
                
                # Check if artwork is already sold
                if artwork.sold:
                    messages.error(request, f'Sorry, "{artwork.title}" has already been sold.')
                    request.session.pop('quick_purchase', None)
                    return redirect('artworks')
                
                artwork_data = {
                    'id': artwork.id,
                    'title': artwork.title,
                    'artist': artwork.artist.full_name,
                    'price': float(artwork.price) if artwork.price else 0,
                    'image': artwork.primary_image,
                    'medium': artwork.medium,
                    'dimensions': artwork.dimensions
                }
                artwork_ids.append(artwork.id)
            else:
                # Use guest checkout data
                artwork_data = guest_checkout_item
                artwork_ids.append(artwork_data['id'])
            
            cart_items.append({
                'artwork': artwork_data,
                'quantity': 1
            })
            subtotal = float(artwork_data['price']) if artwork_data['price'] else 0
            
        except Artwork.DoesNotExist:
            messages.error(request, 'The selected artwork is no longer available.')
            request.session.pop('quick_purchase', None)
            return redirect('artworks')
    else:
        # Process cart items
        for artwork_id, item_data in cart.items():
            try:
                # Get artwork
                artwork = Artwork.objects.get(id=artwork_id, is_active=True)
                
                # Check if artwork is already sold
                if artwork.sold:
                    messages.error(request, f'Sorry, "{artwork.title}" has already been sold.')
                    # Remove from cart
                    if str(artwork_id) in cart:
                        del cart[str(artwork_id)]
                        request.session['cart'] = cart
                    continue
                
                artwork_data = {
                    'id': artwork.id,
                    'title': artwork.title,
                    'artist': artwork.artist.full_name,
                    'price': float(artwork.price) if artwork.price else 0,
                    'image': artwork.primary_image,
                    'medium': artwork.medium,
                    'dimensions': artwork.dimensions
                }
                quantity = item_data.get('quantity', 1)
                cart_items.append({
                    'artwork': artwork_data,
                    'quantity': quantity
                })
                subtotal += float(artwork.price) if artwork.price else 0
                artwork_ids.append(artwork.id)
            except Artwork.DoesNotExist:
                continue
    
    # Check if there are items to process
    if not cart_items:
        messages.error(request, 'No items to checkout.')
        return redirect('cart')
    
    try:
        # MARK ARTWORKS AS SOLD (but keep them visible)
        for artwork_id in artwork_ids:
            try:
                artwork = Artwork.objects.get(id=artwork_id)
                # Only mark as sold if not already sold
                if not artwork.sold:
                    artwork.mark_as_sold()
                    print(f"✅ Marked artwork {artwork_id} ({artwork.title}) as sold")
                else:
                    print(f"⚠️ Artwork {artwork_id} was already sold")
            except Artwork.DoesNotExist:
                print(f"❌ Artwork {artwork_id} not found when marking as sold")
        
        # Calculate totals
        shipping = 500
        tax = subtotal * 0.15
        total = subtotal + shipping + tax
        
        # Generate order reference
        order_reference = request.POST.get('order_reference', 
                                         f"ORD-{timezone.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}")
        
        # Create order data (serializable)
        order_data = {
            'order_reference': order_reference,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'address': address,
            'city': city,
            'country': country,
            'province': province,
            'postal_code': postal_code,
            'payment_method': payment_method,
            'items': cart_items,
            'subtotal': float(subtotal),
            'shipping': float(shipping),
            'tax': float(tax),
            'total': float(total),
            'created_at': timezone.now().isoformat(),
            'artwork_ids': artwork_ids
        }
        
        # Clear cart and quick purchase
        request.session['cart'] = {}
        request.session.pop('quick_purchase', None)
        request.session.pop('guest_checkout_item', None)
        request.session.pop('cart_count', None)
        
        # Store order in session for confirmation (temporary)
        request.session['last_order'] = order_data
        
        # SEND CONFIRMATION EMAIL USING TEMPLATE
        if email:
            try:
                from django.template.loader import render_to_string
                
                # Render HTML email template
                html_message = render_to_string('gallery/emails/order_confirmation_email.html', {
                    'first_name': first_name,
                    'last_name': last_name,
                    'order_reference': order_reference,
                    'order_date': timezone.now().strftime('%B %d, %Y'),
                    'items': cart_items,
                    'subtotal': float(subtotal),
                    'shipping': float(shipping),
                    'tax': float(tax),
                    'total': float(total),
                    'address': address,
                    'city': city,
                    'province': province,
                    'postal_code': postal_code,
                    'country': country,
                    'site_url': request.build_absolute_uri('/')[:-1],
                })
                
                # Create plain text version
                plain_message = f"""
                Thank you for your order #{order_reference} at Camps Bay Gallery!
                
                Order Summary:
                ==============
                Order Number: {order_reference}
                Date: {timezone.now().strftime('%B %d, %Y')}
                
                Items Purchased (Now Marked as Sold):
                ----------------------------
                {chr(10).join([f"- {item['artwork']['title']} by {item['artwork']['artist']}: R {float(item['artwork']['price']):.2f} (Qty: {item['quantity']})" for item in cart_items])}
                
                Subtotal: R {float(subtotal):.2f}
                Shipping: R {float(shipping):.2f}
                Tax (15%): R {float(tax):.2f}
                Total: R {float(total):.2f}
                
                Shipping Address:
                -----------------
                {first_name} {last_name}
                {address}
                {city}, {province} {postal_code}
                {country}
                
                Note: These artworks have been marked as SOLD and will remain visible on our website. 
                We will contact you within 24 hours regarding shipping details.
                
                Thank you for supporting local artists!
                
                Warm regards,
                The Camps Bay Gallery Team
                """
                
                # Send email using Django's send_mail
                send_mail(
                    subject=f'Order Confirmation #{order_reference} - Camps Bay Gallery',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )
                print(f"✅ Order confirmation email sent to {email}")
                
            except Exception as e:
                print(f"❌ Email error details: {str(e)}")
                # Log the error but don't crash the checkout
                messages.warning(request, 'Order placed successfully, but there was an issue sending the confirmation email.')
        
        # Success message and redirect
        messages.success(request, f'Order #{order_reference} placed successfully! The artworks have been marked as SOLD and will remain visible on the website.')
        return redirect('order_confirmation', order_ref=order_reference)
        
    except Exception as e:
        print(f"❌ Checkout error: {str(e)}")
        messages.error(request, 'There was an error processing your order. Please try again.')
        return redirect('checkout')


 
def order_confirmation(request, order_ref):
    """Order confirmation page"""
    order_data = request.session.get('last_order', {})
    
    if not order_data or order_data.get('order_reference') != order_ref:
        messages.error(request, 'Order not found.')
        return redirect('home')
    
    context = {
        'order': order_data,
        'order_ref': order_ref
    }
    return render(request, 'gallery/order_confirmation.html', context)

def update_cart_item(request, artwork_id):
    """Update cart item quantity (AJAX) - updated for guest users"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
            
            cart = request.session.get('cart', {})
            
            if str(artwork_id) in cart:
                # Since artworks are unique, max quantity is 1
                cart[str(artwork_id)]['quantity'] = min(quantity, 1)
                request.session['cart'] = cart
                
                # Update cart count
                cart_count = len(cart)
                request.session['cart_count'] = cart_count
                
                return JsonResponse({'success': True, 'cart_count': cart_count})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})

def remove_from_cart(request, artwork_id):
    """Remove item from cart (AJAX) - updated for guest users"""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        if str(artwork_id) in cart:
            del cart[str(artwork_id)]
            request.session['cart'] = cart
            
            # Update cart count
            cart_count = len(cart)
            request.session['cart_count'] = cart_count
            
            return JsonResponse({'success': True, 'cart_count': cart_count})
    
    return JsonResponse({'success': False})


@login_required
@user_passes_test(is_owner)
def mark_as_sold(request, artwork_id):
    """Admin function to manually mark artwork as sold"""
    try:
        artwork = Artwork.objects.get(id=artwork_id)
        artwork.mark_as_sold()
        messages.success(request, f'"{artwork.title}" has been marked as sold.')
    except Artwork.DoesNotExist:
        messages.error(request, 'Artwork not found.')
    
    return redirect('view_artworks')

@login_required
@user_passes_test(is_owner)
def mark_as_available(request, artwork_id):
    """Admin function to mark artwork as available again"""
    try:
        artwork = Artwork.objects.get(id=artwork_id)
        artwork.sold = False
        artwork.is_active = True
        artwork.availability = 'available'
        artwork.save()
        messages.success(request, f'"{artwork.title}" has been marked as available.')
    except Artwork.DoesNotExist:
        messages.error(request, 'Artwork not found.')
    
    return redirect('view_artworks')