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
    CustomForgotPasswordForm, CustomResetPasswordForm, UserProfileForm, ArtworkForm
)
from .models import User, OTP, UserProfile, Artist, Artwork
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import ArtistForm
# Add this import at the top of views.py with other imports
import random

# ============================================================================
# GLOBAL DATA
# ============================================================================


# Sample artist data
ARTISTS_DATA = [
    {
        'id': 1,
        'name': 'Amara Thompson',
        'image': 'https://images.unsplash.com/photo-1544717305-2782549b5136?w=800&h=800&fit=crop',
        'specialty': 'Abstract & Contemporary',
        'location': 'Cape Town, South Africa',
        'email': 'amara@example.com',
        'bio': 'Amara Thompson\'s work explores the intersection of memory and landscape through abstract forms. Her Coastal Abstractions series has been exhibited internationally and captures the ephemeral quality of light on water.',
        'artworks': [
            {
                'title': 'Coastal Abstractions',
                'image': 'https://images.unsplash.com/photo-1549887534-1541e9326642?w=800&h=800&fit=crop',
                'medium': 'Acrylic on canvas',
                'year': '2025'
            }
        ]
    },
    {
        'id': 2,
        'name': 'Marcus Chen',
        'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=800&fit=crop',
        'specialty': 'Sculpture & Installation',
        'location': 'Johannesburg, South Africa',
        'email': 'marcus@example.com',
        'bio': 'Marcus Chen creates sculptural forms that explore equilibrium and tension in contemporary society. His work in steel and found objects has been featured in major South African galleries.',
        'artworks': [
            {
                'title': 'Equilibrium III',
                'image': 'https://images.unsplash.com/photo-1561214115-f2f134cc4912?w=800&h=800&fit=crop',
                'medium': 'Steel and glass',
                'year': '2024'
            }
        ]
    },
    {
        'id': 3,
        'name': 'Sofia Rodriguez',
        'image': 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=800&h=800&fit=crop',
        'specialty': 'Urban Landscape',
        'location': 'Buenos Aires, Argentina',
        'email': 'sofia@example.com',
        'bio': 'Sofia Rodriguez captures the fragmented beauty of urban environments. Her City Fragments series juxtaposes architectural elements with human presence, exploring themes of isolation and connection in modern cities.',
        'artworks': [
            {
                'title': 'City Fragments',
                'image': 'https://images.unsplash.com/photo-1578301978018-3005759f48f7?w=800&h=800&fit=crop',
                'medium': 'Oil on canvas',
                'year': '2025'
            }
        ]
    },
    {
        'id': 4,
        'name': 'James Williams',
        'image': 'https://images.unsplash.com/photo-1531891437562-4301cf35b7e4?w=800&h=800&fit=crop',
        'specialty': 'Mixed Media',
        'location': 'London, UK',
        'email': 'james@example.com',
        'bio': 'James Williams combines traditional painting techniques with digital media to create works that question our relationship with technology. His pieces have been acquired by major contemporary art collections.',
        'artworks': []
    },
    {
        'id': 5,
        'name': 'Zara Okafor',
        'image': 'https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=800&h=800&fit=crop',
        'specialty': 'Portraiture & Identity',
        'location': 'Lagos, Nigeria',
        'email': 'zara@example.com',
        'bio': 'Zara Okafor\'s portraiture explores themes of identity, diaspora, and cultural heritage. Her vibrant use of color and pattern has made her one of Africa\'s most exciting emerging artists.',
        'artworks': []
    },
    {
        'id': 6,
        'name': 'Kai Nakamura',
        'image': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=800&h=800&fit=crop',
        'specialty': 'Digital & Experimental',
        'location': 'Tokyo, Japan',
        'email': 'kai@example.com',
        'bio': 'Kai Nakamura pushes the boundaries of digital art, creating immersive experiences that blend traditional Japanese aesthetics with cutting-edge technology.',
        'artworks': []
    }
]

# GLOBAL ARTWORK DATA
GLOBAL_ARTWORKS_DATA = [
    {
        'id': 1,
        'title': 'Coastal Abstractions',
        'artist': 'Amara Thompson',
        'artist_id': 1,
        'description': 'A meditation on the meeting of land and sea. Thompson captures the essence of Camps Bay through layered textures and a palette drawn from the coastal landscape.',
        'medium': 'Mixed Media on Canvas',
        'dimensions': '120 × 100 cm',
        'year': '2025',
        'image': 'https://images.unsplash.com/photo-1549887534-1541e9326642?w=800&h=800&fit=crop',
        'data_index': 0,
        'availability': 'at_gallery',
        'sold': False,
        'show_price': True,
        'price': 8500,
        'discounted_price': None,
        'allow_purchase': True,
        'allow_inquiry': True,
        'allow_schedule_viewing': True
    },
    {
        'id': 2,
        'title': 'Equilibrium III',
        'artist': 'Marcus Chen',
        'artist_id': 2,
        'description': "Part of Chen's ongoing exploration of balance and form. This sculptural work plays with weight, shadow, and the negative space between elements.",
        'medium': 'Bronze Sculpture',
        'dimensions': '85 × 45 × 30 cm',
        'year': '2024',
        'image': 'https://images.unsplash.com/photo-1561214115-f2f134cc4912?w=800&h=800&fit=crop',
        'data_index': 1,
        'availability': 'available',
        'sold': False,
        'show_price': False,
        'price': 12000,
        'discounted_price': None,
        'allow_purchase': True,
        'allow_inquiry': False,
        'allow_schedule_viewing': True
    },
    {
        'id': 3,
        'title': 'City Fragments',
        'artist': 'Sofia Rodriguez',
        'artist_id': 3,
        'description': 'Rodriguez deconstructs urban landscapes into geometric fragments, revealing the hidden patterns and rhythms of contemporary life.',
        'medium': 'Acrylic on Canvas',
        'dimensions': '150 × 120 cm',
        'year': '2025',
        'image': 'https://images.unsplash.com/photo-1578301978018-3005759f48f7?w=800&h=800&fit=crop',
        'data_index': 2,
        'availability': 'on_request',
        'sold': False,
        'show_price': False,
        'price': 9500,
        'discounted_price': None,
        'allow_purchase': False,
        'allow_inquiry': True,
        'allow_schedule_viewing': False
    },
    {
        'id': 4,
        'title': 'Silent Spaces',
        'artist': 'James Williams',
        'artist_id': 4,
        'description': 'A minimalist exploration of emptiness and presence. Williams invites contemplation through carefully considered negative space and subtle tonal shifts.',
        'medium': 'Oil on Linen',
        'dimensions': '100 × 100 cm',
        'year': '2024',
        'image': 'https://images.unsplash.com/photo-1547826039-bfc35e0f1ea8?w=800&h=800&fit=crop',
        'data_index': 3,
        'availability': 'at_gallery',
        'sold': True,
        'show_price': True,
        'price': 6800,
        'discounted_price': None,
        'allow_purchase': False,
        'allow_inquiry': True,
        'allow_schedule_viewing': False
    },
    {
        'id': 5,
        'title': 'Earth Memory',
        'artist': 'Zara Okafor',
        'artist_id': 5,
        'description': "Okafor's textured surfaces evoke geological time and ancient landscapes. Each layer tells a story of transformation and permanence.",
        'medium': 'Mixed Media with Natural Pigments',
        'dimensions': '110 × 90 cm',
        'year': '2025',
        'image': 'https://images.unsplash.com/photo-1536924940846-227afb31e2a5?w=800&h=800&fit=crop',
        'data_index': 4,
        'availability': 'available',
        'sold': False,
        'show_price': True,
        'price': 7200,
        'discounted_price': 5800,
        'allow_purchase': True,
        'allow_inquiry': True,
        'allow_schedule_viewing': True
    },
    {
        'id': 6,
        'title': 'Presence',
        'artist': 'Kai Nakamura',
        'artist_id': 6,
        'description': "A contemporary take on portraiture that questions identity and perception. Nakamura's work exists between representation and abstraction.",
        'medium': 'Digital Print on Archival Paper',
        'dimensions': '130 × 95 cm',
        'year': '2025',
        'image': 'https://images.unsplash.com/photo-1579762715118-a6f1d4b934f1?w=800&h=800&fit=crop',
        'data_index': 5,
        'availability': 'at_gallery',
        'sold': False,
        'show_price': True,
        'price': 3200,
        'discounted_price': None,
        'allow_purchase': True,
        'allow_inquiry': True,
        'allow_schedule_viewing': True
    }
]

# ============================================================================
# BASIC VIEWS
# ============================================================================

# [file name]: views.py
# Replace these lines at the top of views.py
# ============================================================================
# GLOBAL DATA - REMOVE ARTISTS_DATA
# ============================================================================

# Remove the entire ARTISTS_DATA list and replace with database queries

# ============================================================================
# BASIC VIEWS
# ============================================================================

# Update the home function:
def home(request):
    """Render the homepage"""
    # Get featured artworks from database (newest 3)
    featured_artworks_db = Artwork.objects.filter(is_active=True).order_by('-created_at')[:3]
    
    # Format for template
    featured_artworks = []
    for artwork in featured_artworks_db:
        featured_artworks.append({
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
    
    # Get active artists from database (limit to 6 for carousel)
    artists = Artist.objects.filter(is_active=True).order_by('first_name')[:6]
    
    context = {
        'featured_artworks': featured_artworks,
        'artists': artists
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




def artworks(request):
    """Render the artworks page from database"""
    artist_filter = request.GET.get('artist', 'all')
    sort_by = request.GET.get('sort', 'newest')
    
    # Get active artworks from database
    artworks_list = Artwork.objects.filter(is_active=True).select_related('artist')
    
    if artist_filter != 'all':
        try:
            # Try to get artist by ID or name
            if artist_filter.isdigit():
                artworks_list = artworks_list.filter(artist_id=artist_filter)
            else:
                # Handle artist name filter
                artworks_list = artworks_list.filter(
                    Q(artist__first_name__icontains=artist_filter) |
                    Q(artist__last_name__icontains=artist_filter)
                )
        except:
            pass
    
    # Apply sorting
    if sort_by == 'newest':
        artworks_list = artworks_list.order_by('-year', '-created_at')
    elif sort_by == 'oldest':
        artworks_list = artworks_list.order_by('year', 'created_at')
    elif sort_by == 'title_asc':
        artworks_list = artworks_list.order_by('title')
    elif sort_by == 'title_desc':
        artworks_list = artworks_list.order_by('-title')
    elif sort_by == 'price_low':
        artworks_list = artworks_list.order_by('price')
    elif sort_by == 'price_high':
        artworks_list = artworks_list.order_by('-price')
    
    # Format for template
    formatted_artworks = []
    for artwork in artworks_list:
        formatted_artworks.append({
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
    
    # Get unique artists for filter
    unique_artists = Artist.objects.filter(is_active=True).order_by('first_name', 'last_name')
    
    context = {
        'artworks': formatted_artworks,
        'artists': unique_artists,
        'current_artist': artist_filter,
        'current_sort': sort_by,
        'total_artworks': len(formatted_artworks),
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
# CART & CHECKOUT VIEWS
# ============================================================================

@login_required
def add_to_cart(request, artwork_id):
    """Add artwork to cart"""
    if request.method == 'POST':
        # Get the artwork from global data
        artwork = None
        for a in GLOBAL_ARTWORKS_DATA:
            if a['id'] == artwork_id:
                artwork = a
                break
        
        if not artwork:
            messages.error(request, 'Artwork not found.')
            return redirect('artworks')
        
        # Get or create cart in session
        cart = request.session.get('cart', {})
        
        # Since each artwork is unique, we can only have 1 of each
        if str(artwork_id) not in cart:
            cart[str(artwork_id)] = {
                'quantity': 1,
                'added_at': timezone.now().isoformat()
            }
            request.session['cart'] = cart
            messages.success(request, f'"{artwork["title"]}" added to cart.')
        else:
            messages.info(request, f'"{artwork["title"]}" is already in your cart.')
        
        # Check where to redirect
        redirect_to = request.POST.get('redirect_to', 'cart')
        
        if redirect_to == 'checkout':
            return redirect('checkout')
        else:
            return redirect('cart')
    
    return redirect('artworks')

@login_required
def cart_view(request):
    """View shopping cart"""
    cart = request.session.get('cart', {})
    
    cart_items = []
    subtotal = 0
    
    for artwork_id, item_data in cart.items():
        for artwork in GLOBAL_ARTWORKS_DATA:
            if artwork['id'] == int(artwork_id):
                quantity = item_data.get('quantity', 1)
                item_total = artwork.get('price', 0) * quantity
                subtotal += item_total
                
                cart_items.append({
                    'artwork': artwork,
                    'quantity': quantity,
                    'item_total': item_total
                })
                break
    
    # Calculate totals
    shipping = 500
    tax = subtotal * 0.15
    total = subtotal + shipping + tax
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'item_count': len(cart_items)
    }
    
    return render(request, 'gallery/cart.html', context)

@login_required
def checkout_view(request):
    """Checkout page"""
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.info(request, 'Your cart is empty. Add items before checkout.')
        return redirect('cart')
    
    cart_items = []
    subtotal = 0
    
    for artwork_id, item_data in cart.items():
        for artwork in GLOBAL_ARTWORKS_DATA:
            if artwork['id'] == int(artwork_id):
                quantity = item_data.get('quantity', 1)
                item_total = artwork.get('price', 0) * quantity
                subtotal += item_total
                
                cart_items.append({
                    'artwork': artwork,
                    'quantity': quantity,
                    'item_total': item_total
                })
                break
    
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
        'item_count': len(cart_items)
    }
    
    return render(request, 'gallery/checkout.html', context)

@login_required
def process_checkout(request):
    """Process checkout (simplified version)"""
    if request.method == 'POST':
        # In a real application, you would:
        # 1. Validate the form data
        # 2. Create an order record in the database
        # 3. Process payment (via Stripe, PayPal, etc.)
        # 4. Clear the cart
        # 5. Send confirmation email
        
        # For now, just clear the cart and show success message
        request.session['cart'] = {}
        messages.success(request, 'Order placed successfully! Thank you for your purchase.')
        
        return redirect('home')
    
    return redirect('checkout')

@login_required
def update_cart_item(request, artwork_id):
    """Update cart item quantity (AJAX)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
            
            cart = request.session.get('cart', {})
            
            if str(artwork_id) in cart:
                # Since artworks are unique, max quantity is 1
                cart[str(artwork_id)]['quantity'] = min(quantity, 1)
                request.session['cart'] = cart
                
                return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})

@login_required
def remove_from_cart(request, artwork_id):
    """Remove item from cart (AJAX)"""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        if str(artwork_id) in cart:
            del cart[str(artwork_id)]
            request.session['cart'] = cart
            
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})