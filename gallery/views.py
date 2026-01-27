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
    CustomForgotPasswordForm, CustomResetPasswordForm, UserProfileForm
)
from .models import User, OTP, UserProfile, Artist
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import ArtistForm



# Sample artist data (in production, this would come from a database)
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

def home(request):
    """Render the homepage"""
    return render(request, 'gallery/index.html')

def about(request):
    """Render the about page"""
    return render(request, 'gallery/about.html')

def artists(request):
    """Render the artists overview page"""
    context = {
        'artists': ARTISTS_DATA
    }
    return render(request, 'gallery/artists.html', context)

def artist_detail(request, artist_id):
    """Render individual artist detail page"""
    # Find the artist with the matching ID
    artist = None
    for a in ARTISTS_DATA:
        if a['id'] == artist_id:
            artist = a
            break
    
    if not artist:
        # If artist not found, redirect to artists overview
        from django.shortcuts import redirect
        return redirect('artists')
    
    context = {
        'artist': artist
    }
    return render(request, 'gallery/artist_detail.html', context)

def artworks(request):
    """Render the artworks page"""
    # Get filter and sort parameters from request
    artist_filter = request.GET.get('artist', 'all')
    sort_by = request.GET.get('sort', 'newest')
    
    # Reuse the exact same artwork data structure from main.js
    ARTWORKS_DATA = [
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
            'data_index': 0
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
            'data_index': 1
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
            'data_index': 2
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
            'data_index': 3
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
            'data_index': 4
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
            'data_index': 5
        },
        {
            'id': 7,
            'title': 'Linear Tensions',
            'artist': 'Amara Thompson',
            'artist_id': 1,
            'description': 'Thompson returns to geometric abstraction, creating visual tension through intersecting lines and carefully balanced composition.',
            'medium': 'Acrylic and Graphite on Canvas',
            'dimensions': '140 × 110 cm',
            'year': '2024',
            'image': 'https://images.unsplash.com/photo-1577083288073-40892c0860fd?w=800&h=800&fit=crop',
            'data_index': 6
        },
        {
            'id': 8,
            'title': 'Flow State',
            'artist': 'Marcus Chen',
            'artist_id': 2,
            'description': "Chen's organic forms seem to move and breathe. This piece captures a moment of transformation, frozen in bronze.",
            'medium': 'Bronze Sculpture',
            'dimensions': '95 × 60 × 40 cm',
            'year': '2025',
            'image': 'https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800&h=800&fit=crop',
            'data_index': 7
        },
        {
            'id': 9,
            'title': 'Layered Narratives',
            'artist': 'Sofia Rodriguez',
            'artist_id': 3,
            'description': 'Rodriguez weaves together fragments of text, image, and paint to create a rich tapestry of meaning and memory.',
            'medium': 'Mixed Media Collage',
            'dimensions': '125 × 100 cm',
            'year': '2025',
            'image': 'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=800&h=800&fit=crop',
            'data_index': 8
        },
    ]
    
    # Get unique artists for filter dropdown
    unique_artists = sorted(set([artwork['artist'] for artwork in ARTWORKS_DATA]))
    
    # Filter by artist if selected
    filtered_artworks = ARTWORKS_DATA
    if artist_filter != 'all':
        filtered_artworks = [artwork for artwork in ARTWORKS_DATA if artwork['artist'] == artist_filter]
    
    # Sort artworks (simplified to match your request)
    if sort_by == 'newest':
        filtered_artworks = sorted(filtered_artworks, key=lambda x: x['year'], reverse=True)
    elif sort_by == 'oldest':
        filtered_artworks = sorted(filtered_artworks, key=lambda x: x['year'])
    elif sort_by == 'title_asc':
        filtered_artworks = sorted(filtered_artworks, key=lambda x: x['title'].lower())
    elif sort_by == 'title_desc':
        filtered_artworks = sorted(filtered_artworks, key=lambda x: x['title'].lower(), reverse=True)
    
    context = {
        'artworks': filtered_artworks,
        'artists': unique_artists,
        'current_artist': artist_filter,
        'current_sort': sort_by,
        'total_artworks': len(filtered_artworks),
    }
    
    return render(request, 'gallery/artworks.html', context)

def contact(request):
    """Render the contact page"""
    return render(request, 'gallery/contact.html')

def google_login_redirect(request):
    """Redirect to Google OAuth login via allauth"""
    return redirect('account_login')

# ============================================================================
# AUTHENTICATION VIEWS - SIMPLIFIED & EFFICIENT
# ============================================================================

def login_view(request):
    """Simple login view - handles both modal and full-page requests"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomLoginForm(request.POST, request=request)  # FIXED: Pass request to form
        if form.is_valid():
            # Form's clean method already authenticated and set user_cache
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
        form = CustomLoginForm(request=request)  # FIXED: Pass request to form
    
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
                # Create user
                user = form.save(commit=False)
                user.is_email_verified = False
                user.save()
                
                # Generate OTP
                otp_code = OTP.generate_otp()
                expires_at = timezone.now() + timedelta(minutes=15)
                
                OTP.objects.create(
                    user=user,
                    otp_code=otp_code,
                    otp_type='email_verification',
                    expires_at=expires_at
                )
                
                # Store in session
                request.session['pending_user_id'] = user.id
                request.session['pending_user_email'] = user.email
                
                # ============================================================
                # SIMPLIFIED EMAIL SENDING (Like Crafted Thrift)
                # ============================================================
                
                # Build verification URL
                verification_url = request.build_absolute_uri(reverse('verify_email'))
                
                # Render email template
                html_message = render_to_string('gallery/emails/verify_email_email.html', {
                    'user': user,
                    'otp_code': otp_code,
                    'verification_url': verification_url,
                })
                
                # Plain text fallback
                plain_message = f"""
                Hello {user.first_name},
                
                Your verification code is: {otp_code}
                
                Enter this code to activate your account.
                Code expires in 15 minutes.
                
                Camps Bay Gallery Team
                """
                
                # Send email directly
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
            
            # Mark email as verified
            user.is_email_verified = True
            user.save()
            
            # Clear session
            del request.session['pending_user_id']
            del request.session['pending_user_email']
            
            # FIXED: Specify which backend to use when logging in
            # When you have multiple backends, you must specify which one to use
            from django.contrib.auth import login
            
            # IMPORTANT: Manually set the backend attribute on the user
            # We'll use the first authentication backend from settings
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            
            # Now login will work
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
                
                # Generate OTP for password reset
                otp_code = OTP.generate_otp()
                expires_at = timezone.now() + timedelta(minutes=15)
                
                # Delete old OTPs
                OTP.objects.filter(user=user, otp_type='password_reset').delete()
                
                # Create new OTP
                OTP.objects.create(
                    user=user,
                    otp_code=otp_code,
                    otp_type='password_reset',
                    expires_at=expires_at
                )
                
                # Store in session
                request.session['reset_user_id'] = user.id
                
                # ============================================================
                # SIMPLIFIED PASSWORD RESET EMAIL
                # ============================================================
                
                # Build reset URL
                reset_url = request.build_absolute_uri(reverse('reset_password_verify'))
                
                # Render email template
                html_message = render_to_string('gallery/emails/password_reset.html', {
                    'user': user,
                    'otp_code': otp_code,
                    'reset_url': reset_url,
                })
                
                # Plain text fallback
                plain_message = f"""
                Hello {user.first_name},
                
                Your password reset code is: {otp_code}
                
                Enter this code to reset your password.
                Code expires in 15 minutes.
                
                Camps Bay Gallery Team
                """
                
                # Send email directly
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
            
            # Mark OTP as verified in session
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
            # Clear session
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
    """User profile page - Simple and clean"""
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
        
        # Delete existing unused OTPs
        OTP.objects.filter(user=user, otp_type=otp_type, is_used=False).delete()
        
        # Generate new OTP
        otp_code = OTP.generate_otp()
        expires_at = timezone.now() + timedelta(minutes=15)
        
        OTP.objects.create(
            user=user,
            otp_code=otp_code,
            otp_type=otp_type,
            expires_at=expires_at
        )
        
        # Determine email type
        if otp_type == 'email_verification':
            subject = 'New Verification Code - Camps Bay Gallery'
            # Build verification URL
            verification_url = request.build_absolute_uri(reverse('verify_email'))
            
            # Render email template
            html_message = render_to_string('gallery/emails/verify_email_email.html', {
                'user': user,
                'otp_code': otp_code,
                'verification_url': verification_url,
            })
        else:
            subject = 'New Password Reset Code - Camps Bay Gallery'
            # Build reset URL
            reset_url = request.build_absolute_uri(reverse('reset_password_verify'))
            
            # Render email template
            html_message = render_to_string('gallery/emails/password_reset.html', {
                'user': user,
                'otp_code': otp_code,
                'reset_url': reset_url,
            })
        
        # Plain text fallback
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
# PLACEHOLDER VIEWS FOR FUTURE ADMIN FEATURES
# ============================================================================

@login_required
def manage_artists_view(request):
    """Placeholder view for managing artists - FUTURE FEATURE"""
    if not request.user.is_owner:
        messages.error(request, 'Access denied. Admin features are for owners only.')
        return redirect('home')
    
    messages.info(request, 'Manage Artists feature is coming soon!')
    return redirect('admin_dashboard')


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
    
    # Placeholder for future orders system
    messages.info(request, 'Order history feature is coming soon!')
    
    if request.user.is_owner:
        return redirect('admin_dashboard')
    else:
        return redirect('profile')


# Helper function to check if user is owner
def is_owner(user):
    return user.is_authenticated and user.is_owner

# Add these views at the bottom of views.py, before the last line

# ============================================================================
# ARTIST MANAGEMENT VIEWS
# ============================================================================

@login_required
@user_passes_test(is_owner)
def add_artist_view(request):
    """Add a new artist to the database"""
    if request.method == 'POST':
        form = ArtistForm(request.POST, request.FILES)
        if form.is_valid():
            artist = form.save()
            messages.success(request, f'Artist "{artist.first_name} {artist.last_name}" added successfully!')
            return redirect('view_artists')
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
    
    # Get all active artists by default
    artists = Artist.objects.all().order_by('first_name', 'last_name')
    
    # Apply search filter if query exists
    if search_query:
        artists = artists.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(specialty__icontains=search_query) |
            Q(bio__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(artists, 12)  # Show 12 artists per page
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
        
        # Handle image removal
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
        
        # Delete the artist
        artist.delete()
        
        messages.success(request, f'Artist "{artist_name}" deleted successfully!')
        
    except Artist.DoesNotExist:
        messages.error(request, 'Artist not found.')
    
    return redirect('view_artists')


# Update the placeholder manage_artists_view to redirect to view_artists
@login_required
def manage_artists_view(request):
    """Redirect to view artists page"""
    if not request.user.is_owner:
        messages.error(request, 'Access denied. Admin features are for owners only.')
        return redirect('home')
    
    return redirect('view_artists')