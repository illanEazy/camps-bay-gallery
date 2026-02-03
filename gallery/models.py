from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import random
import string

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'owner')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

# Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('owner', 'Owner'),
    )
    
    username = None  # Remove username field
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.email
    
    @property
    def is_customer(self):
        return self.role == 'customer'
    
    @property
    def is_owner(self):
        return self.role == 'owner'

# OTP Model for Email Verification and Password Reset
class OTP(models.Model):
    OTP_TYPE_CHOICES = (
        ('email_verification', 'Email Verification'),
        ('password_reset', 'Password Reset'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, choices=OTP_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_used(self):
        self.is_used = True
        self.save()
    
    @classmethod
    def generate_otp(cls):
        return ''.join(random.choices(string.digits, k=6))
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'otp_type', 'is_used']),
        ]

# User Profile Model (for additional user information)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    newsletter_subscription = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.email}'s Profile"

# models.py - SIMPLIFIED ARTIST MODEL
class Artist(models.Model):
    """Artist model for storing artist information in the database"""
    
    # Basic Information - Required
    first_name = models.CharField(
        max_length=100,
        verbose_name='First Name',
        help_text='Required. Enter the artist\'s first name.'
    )
    
    # Basic Information - Optional
    last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Last Name',
        help_text='Optional. Enter the artist\'s last name.'
    )
    
    # Location
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Location'
    )
    
    # NEW FIELDS: Medium, Style, Theme
    medium = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Medium',
        help_text='Optional. Artistic medium (e.g., Oil, Acrylic, Collage)'
    )
    
    style = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Style',
        help_text='Optional. Artistic style (e.g., Figurative, Contemporary)'
    )
    
    theme = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Theme',
        help_text='Optional. Artistic themes (e.g., Identity, Urban Life)'
    )
    
    # Biography
    bio = models.TextField(
        blank=True,
        verbose_name='Biography'
    )
    
    # Profile Images
    profile_picture = models.ImageField(
        upload_to='artists/profile_pictures/',
        blank=True,
        null=True,
        verbose_name='Profile Picture'
    )
    image_url = models.URLField(
        blank=True,
        verbose_name='Image URL'
    )
    
    # Status Field
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """String representation of the artist"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    @property
    def full_name(self):
        """Get full name of artist"""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    @property
    def image(self):
        """Get the primary image for the artist"""
        if self.profile_picture:
            return self.profile_picture.url
        elif self.image_url:
            return self.image_url
        else:
            return '/static/gallery/images/default-artist.jpg'  # You should create this
    
    @property
    def name(self):
        """Get the full name (for compatibility with existing code)"""
        return self.full_name
    
    class Meta:
        ordering = ['first_name', 'last_name']
        verbose_name = 'Artist'
        verbose_name_plural = 'Artists'

# ============================================================================
# ARTWORK MODEL - CONNECTED TO ARTIST
# ============================================================================

class Artwork(models.Model):
    """Artwork model for storing artwork information in the database"""
    
    # AVAILABILITY CHOICES - EXACT MATCH TO FRONTEND
    AVAILABILITY_CHOICES = (
        ('at_gallery', 'Available at Gallery'),
        ('available', 'Available'),
        ('on_request', 'Available on Request'),
    )
    
    # REQUIRED: ForeignKey to Artist (One Artist -> Many Artworks)
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='artworks',
        verbose_name='Artist',
        help_text='Required. Select the artist who created this artwork.'
    )
    
    # REQUIRED: Basic Information
    title = models.CharField(
        max_length=200,
        verbose_name='Artwork Title',
        help_text='Required. Enter the title of the artwork.'
    )
    
    # REQUIRED: Availability Status
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='available',
        verbose_name='Availability Status',
        help_text='How this artwork can be acquired by customers.'
    )
    
    # Price Information (Conditionally Required)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Price',
        help_text='Required unless "Available on Request". Enter price in local currency.'
    )
    
    discounted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Discounted Price',
        help_text='Optional. Special promotional price.'
    )
    
    # Sold Status
    sold = models.BooleanField(
        default=False,
        verbose_name='Sold',
        help_text='Mark as sold if this artwork has been purchased.'
    )
    
    # Artistic Details (Optional)
    medium = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Medium',
        help_text='Optional. Artistic medium (e.g., Oil on Canvas, Bronze Sculpture)'
    )
    
    dimensions = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Dimensions',
        help_text='Optional. Artwork dimensions (e.g., 120 × 100 cm)'
    )
    
    year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Year',
        help_text='Optional. Year the artwork was created.'
    )
    
    # Description
    description = models.TextField(
        blank=True,
        verbose_name='Description',
        help_text='Optional. Detailed description of the artwork.'
    )
    
    # Images
    image = models.ImageField(
        upload_to='artworks/images/',
        blank=True,
        null=True,
        verbose_name='Artwork Image'
    )
    
    image_url = models.URLField(
        blank=True,
        verbose_name='Image URL',
        help_text='Optional. URL to artwork image if hosted elsewhere.'
    )
    
    # Status Field
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active',
        help_text='Uncheck to hide this artwork from the website.'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='artworks_created',
        verbose_name='Created By'
    )
    
    def __str__(self):
        """String representation of the artwork"""
        return f"{self.title} by {self.artist.full_name}"
    
    @property
    def display_price(self):
        """Get display price with discounted price if available"""
        if self.discounted_price:
            return self.discounted_price
        return self.price
    
    @property
    def has_discount(self):
        """Check if artwork has a discount"""
        return bool(self.discounted_price and self.discounted_price < self.price)
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if applicable"""
        if self.has_discount and self.price:
            discount = ((self.price - self.discounted_price) / self.price) * 100
            return int(discount)
        return 0
    
    @property
    def availability_display(self):
        """Get human-readable availability"""
        return dict(self.AVAILABILITY_CHOICES).get(self.availability, self.availability)
    
    @property
    def show_price(self):
        """Determine if price should be shown based on availability"""
        return self.availability != 'on_request' and not self.sold
    
    @property
    def allow_purchase(self):
        """Determine if purchase is allowed based on availability and sold status"""
        return self.availability in ['available', 'at_gallery'] and not self.sold
    
    @property
    def allow_inquiry(self):
        """Determine if inquiry is allowed"""
        return True  # Always allow inquiries
    
    @property
    def allow_schedule_viewing(self):
        """Determine if schedule viewing is allowed"""
        return self.availability == 'at_gallery' and not self.sold
    
    @property
    def primary_image(self):
        """Get the primary image for the artwork"""
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        else:
            return '/static/gallery/images/default-artwork.jpg'  # You should create this
    
    def clean(self):
        """Custom validation for price fields"""
        from django.core.exceptions import ValidationError
        
        # Price is required unless availability is 'on_request'
        if self.availability != 'on_request' and not self.price:
            raise ValidationError({'price': 'Price is required for artworks that are not "Available on Request".'})
        
        # If discounted_price exists, it must be less than price
        if self.discounted_price and self.price and self.discounted_price >= self.price:
            raise ValidationError({'discounted_price': 'Discounted price must be lower than the regular price.'})
        
        # Year validation (if provided)
        if self.year:
            from datetime import datetime
            current_year = datetime.now().year
            if self.year < 1900 or self.year > current_year + 5:
                raise ValidationError({'year': f'Year must be between 1900 and {current_year + 5}.'})
    
    def save(self, *args, **kwargs):
        """Custom save method"""
        self.full_clean()  # Run validation before saving
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Artwork'
        verbose_name_plural = 'Artworks'
        indexes = [
            models.Index(fields=['artist', 'is_active', 'sold']),
            models.Index(fields=['availability', 'is_active']),
            models.Index(fields=['price']),
        ]
