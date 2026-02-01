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

