from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import User, UserProfile, OTP, Artist, Artwork
from django.utils import timezone
from datetime import timedelta
from django_countries.fields import CountryField
from django_countries import countries
import re



# Custom Login Form - FIXED TO ACCEPT REQUEST
class CustomLoginForm(forms.Form):
    """Custom login form that doesn't inherit from AuthenticationForm"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email',
            'id': 'email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password',
            'id': 'password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        if email and password:
            if not self.request:
                raise forms.ValidationError("Request context is missing.")
            
            # Authenticate using email
            user = authenticate(self.request, email=email, password=password)
            if user is None:
                raise forms.ValidationError(
                    "Invalid email or password. Please try again.",
                    code='invalid_login',
                )
            elif not user.is_email_verified:
                raise forms.ValidationError(
                    "Please verify your email address before logging in.",
                    code='email_not_verified',
                )
            else:
                self.user_cache = user
        
        return self.cleaned_data

# Custom Signup Form
class CustomSignupForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your first name',
            'id': 'firstName'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your last name',
            'id': 'lastName'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email',
            'id': 'email'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create a password',
            'id': 'password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password',
            'id': 'confirmPassword'
        })
    )
    role = forms.ChoiceField(
        choices=[('customer', 'Customer')],
        initial='customer',
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Don't pop username - it doesn't exist in our form
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        
        # Password validation rules
        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password1):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', password1):
            raise ValidationError("Password must contain at least one number.")
        
        return password1

# OTP Verification Form
class OTPVerificationForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter 6-digit OTP',
            'id': 'otpCode'
        })
    )
    
    def __init__(self, user=None, otp_type=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.otp_type = otp_type
    
    def clean_otp_code(self):
        otp_code = self.cleaned_data.get('otp_code')
        
        if self.user and self.otp_type:
            try:
                otp = OTP.objects.get(
                    user=self.user,
                    otp_code=otp_code,
                    otp_type=self.otp_type,
                    is_used=False
                )
                
                if not otp.is_valid():
                    raise ValidationError("OTP has expired. Please request a new one.")
                
                self.otp_instance = otp
            except OTP.DoesNotExist:
                raise ValidationError("Invalid OTP code. Please check and try again.")
        
        return otp_code

# Forgot Password Form
class CustomForgotPasswordForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address',
            'id': 'email'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user = User.objects.get(email=email)
            if not user.is_email_verified:
                raise ValidationError("Please verify your email address first.")
            self.user = user
        except User.DoesNotExist:
            raise ValidationError("No account found with this email address.")
        return email

# Reset Password Form
class CustomResetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'New password',
            'id': 'newPassword1'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm new password',
            'id': 'newPassword2'
        })
    )

# User Profile Form
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'address', 'city', 'country', 'newsletter_subscription']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Your address...'
            }),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'country': forms.TextInput(attrs={'class': 'form-input'}),
        }


# Artist Form - SIMPLIFIED TO MATCH ADD ARTIST PAGE
class ArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = [
            'first_name', 'last_name', 'location', 
            'medium', 'style', 'theme',  # NEW FIELDS ADDED
            'bio', 'profile_picture', 'image_url', 'is_active'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter first name',
                'id': 'first_name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter last name (optional)',
                'id': 'last_name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter location (optional)',
                'id': 'location'
            }),
            # NEW FIELDS WIDGETS
            'medium': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Oil, Acrylic, Collage (optional)',
                'id': 'medium'
            }),
            'style': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Figurative, Contemporary (optional)',
                'id': 'style'
            }),
            'theme': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Identity, Urban Life (optional)',
                'id': 'theme'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Enter artist biography (optional)',
                'id': 'bio',
                'rows': 6
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter image URL (optional)',
                'id': 'image_url'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields except first_name optional
        self.fields['first_name'].required = True
        self.fields['last_name'].required = False
        self.fields['location'].required = False
        # NEW FIELDS - OPTIONAL
        self.fields['medium'].required = False
        self.fields['style'].required = False
        self.fields['theme'].required = False
        self.fields['bio'].required = False
        self.fields['profile_picture'].required = False
        self.fields['image_url'].required = False
        self.fields['is_active'].required = False
        self.fields['is_active'].initial = True
    
    def clean_image_url(self):
        image_url = self.cleaned_data.get('image_url')
        if image_url:
            # Basic URL validation
            from django.core.validators import URLValidator
            from django.core.exceptions import ValidationError as DjangoValidationError
            
            val = URLValidator()
            try:
                val(image_url)
            except DjangoValidationError:
                raise ValidationError("Please enter a valid URL (include http:// or https://)")
        return image_url


# Artwork Form - MATCHING ADD ARTWORK PAGE
class ArtworkForm(forms.ModelForm):
    # Override price field to be required conditionally
    price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-input price-input',
            'placeholder': 'Enter price',
            'id': 'price',
            'step': '0.01'
        })
    )
    
    discounted_price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-input price-input',
            'placeholder': 'Discounted price (optional)',
            'id': 'discounted_price',
            'step': '0.01'
        })
    )
    
    class Meta:
        model = Artwork
        fields = [
            'artist', 'title', 'availability', 'price', 'discounted_price',
            'sold', 'medium', 'dimensions', 'year', 'description',
            'image', 'image_url', 'is_active'
        ]
        widgets = {
            'artist': forms.Select(attrs={
                'class': 'form-select',
                'id': 'artist',
                'required': True
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter artwork title',
                'id': 'title'
            }),
            'availability': forms.Select(attrs={
                'class': 'form-select',
                'id': 'availability',
                'required': True
            }),
            'medium': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., Oil on Canvas (optional)',
                'id': 'medium'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., 120 × 100 cm (optional)',
                'id': 'dimensions'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g., 2025',
                'id': 'year',
                'min': '1900',
                'max': '2050'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Describe the artwork...',
                'id': 'description',
                'rows': 6
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'Image URL (optional)',
                'id': 'image_url'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get active artists for dropdown
        self.fields['artist'].queryset = Artist.objects.filter(is_active=True).order_by('first_name', 'last_name')
        
        # Make required fields
        self.fields['artist'].required = True
        self.fields['title'].required = True
        self.fields['availability'].required = True
        
        # Make optional fields
        self.fields['medium'].required = False
        self.fields['dimensions'].required = False
        self.fields['year'].required = False
        self.fields['description'].required = False
        self.fields['image'].required = False
        self.fields['image_url'].required = False
        self.fields['is_active'].required = False
        self.fields['sold'].required = False
        
        # Set initial values
        self.fields['is_active'].initial = True
        self.fields['sold'].initial = False
        
        # Add help text
        self.fields['artist'].help_text = 'Select the artist who created this artwork'
        self.fields['availability'].help_text = 'Determines how customers can acquire this artwork'
        
    def clean(self):
        cleaned_data = super().clean()
        availability = cleaned_data.get('availability')
        price = cleaned_data.get('price')
        discounted_price = cleaned_data.get('discounted_price')
        
        # Price validation
        if availability != 'on_request':
            if not price:
                self.add_error('price', 'Price is required for artworks that are not "Available on Request".')
            elif price <= 0:
                self.add_error('price', 'Price must be greater than 0.')
        
        # Discounted price validation
        if discounted_price:
            if not price:
                self.add_error('discounted_price', 'Cannot set discounted price without regular price.')
            elif discounted_price >= price:
                self.add_error('discounted_price', 'Discounted price must be lower than the regular price.')
        
        # Year validation
        year = cleaned_data.get('year')
        if year:
            from datetime import datetime
            current_year = datetime.now().year
            if year < 1900 or year > current_year + 5:
                self.add_error('year', f'Year must be between 1900 and {current_year + 5}.')
        
        return cleaned_data
    
    def clean_image_url(self):
        image_url = self.cleaned_data.get('image_url')
        if image_url:
            # Basic URL validation
            from django.core.validators import URLValidator
            from django.core.exceptions import ValidationError as DjangoValidationError
            
            val = URLValidator()
            try:
                val(image_url)
            except DjangoValidationError:
                raise ValidationError("Please enter a valid URL (include http:// or https://)")
        return image_url


# Add after existing forms
class CheckoutForm(forms.Form):
    """Checkout form with dynamic address fields"""
    
    # Contact Information
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your first name',
            'id': 'firstName'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your last name',
            'id': 'lastName'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email',
            'id': 'email'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your phone number',
            'id': 'phone'
        })
    )
    
    # Shipping Address
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'placeholder': 'Your complete address',
            'rows': 3,
            'id': 'address'
        })
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your city',
            'id': 'city'
        })
    )
    
    # Country Field with all countries
    country = forms.ChoiceField(
        choices=[('', 'Select Country')] + list(countries),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'country',
            'onchange': 'updateProvinceField()'
        })
    )
    
    # Dynamic province/state/region field
    admin_division = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter province/state/region',
            'id': 'adminDivision'
        })
    )
    
    postal_code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter postal code',
            'id': 'postalCode'
        })
    )
    
    # Save address for future orders
    save_address = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
            'id': 'saveAddress'
        })
    )
    
    # Terms agreement
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
            'id': 'terms'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill user data if available
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            
            # Try to get profile data
            try:
                profile = user.profile
                self.fields['address'].initial = profile.address
                self.fields['city'].initial = profile.city
                self.fields['country'].initial = profile.country.code if profile.country else ''
                self.fields['postal_code'].initial = getattr(profile, 'postal_code', '')
            except UserProfile.DoesNotExist:
                pass

# Contact Form - MATCHES ORIGINAL STATIC FORM DESIGN
class ContactForm(forms.Form):
    """Contact form for general inquiries - matches original static form"""
    
    # Contact Information (EXACTLY matches original form)
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your first name',
            'id': 'firstName'
        })
    )
    
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your last name',
            'id': 'lastName'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email',
            'id': 'email'
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Phone number (optional)',
            'id': 'phone'
        })
    )
    
    # Message
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'placeholder': 'Tell us more about your inquiry...',
            'id': 'message',
            'rows': 6
        })
    )
    
    # Newsletter subscription (optional)
    newsletter_subscription = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
            'id': 'newsletter'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill user data if available
        if user and user.is_authenticated:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['phone'].initial = user.phone if hasattr(user, 'phone') else ''