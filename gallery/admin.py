from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, OTP

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_email_verified', 'is_staff', 'is_active')
    list_filter = ('role', 'is_email_verified', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('role', 'is_email_verified', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('created_at', 'updated_at')

# OTP Admin
class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'otp_type', 'created_at', 'expires_at', 'is_used', 'is_valid')
    list_filter = ('otp_type', 'is_used', 'created_at')
    search_fields = ('user__email', 'otp_code')
    readonly_fields = ('created_at', 'expires_at')

# User Profile Admin
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'country', 'newsletter_subscription')
    list_filter = ('country', 'newsletter_subscription')
    search_fields = ('user__email', 'city', 'country')

# Register models
admin.site.register(User, CustomUserAdmin)
admin.site.register(OTP, OTPAdmin)
admin.site.register(UserProfile, UserProfileAdmin)