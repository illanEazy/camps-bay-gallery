from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, OTP, Artist, Artwork

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


# ARTIST ADMIN - SIMPLIFIED TO MATCH OUR FIELDS
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'location', 'medium', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('first_name', 'last_name', 'location', 'bio', 'medium', 'style', 'theme')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'location')
        }),
        ('Artistic Details', {  # NEW SECTION FOR MEDIUM/STYLE/THEME
            'fields': ('medium', 'style', 'theme')
        }),
        ('Biography', {
            'fields': ('bio',)
        }),
        ('Images', {
            'fields': ('profile_picture', 'image_url')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_editable = ('is_active',)


# ARTWORK ADMIN
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'availability', 'price_display', 'sold', 'is_active', 'created_at')
    list_filter = ('availability', 'sold', 'is_active', 'artist', 'created_at')
    search_fields = ('title', 'artist__first_name', 'artist__last_name', 'description', 'medium')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    list_editable = ('sold', 'is_active')
    list_per_page = 20
    
    fieldsets = (
        ('Artist Information', {
            'fields': ('artist', 'created_by')
        }),
        ('Artwork Details', {
            'fields': ('title', 'description')
        }),
        ('Availability & Pricing', {
            'fields': ('availability', 'price', 'discounted_price', 'sold')
        }),
        ('Artistic Information', {
            'fields': ('medium', 'dimensions', 'year')
        }),
        ('Images', {
            'fields': ('image', 'image_url')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_display(self, obj):
        if obj.show_price:
            if obj.has_discount:
                return f"R {obj.discounted_price} (was R {obj.price})"
            return f"R {obj.price}"
        return "Price on Request"
    price_display.short_description = 'Price'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('artist')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # If creating a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# Register models
admin.site.register(User, CustomUserAdmin)
admin.site.register(OTP, OTPAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Artist, ArtistAdmin)  # Add this line
admin.site.register(Artwork, ArtworkAdmin)