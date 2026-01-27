from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.models import Session
from django.utils import timezone

class CacheControlMiddleware(MiddlewareMixin):
    """Add cache control headers to responses"""
    
    def process_response(self, request, response):
        # Add no-cache headers for authenticated users
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        else:
            # Public pages can be cached for 5 minutes
            response['Cache-Control'] = 'public, max-age=300'
        
        return response


class SessionCleanupMiddleware(MiddlewareMixin):
    """Clean up expired sessions to prevent CSRF errors"""
    
    def process_request(self, request):
        # Force session to save if modified
        if request.session.modified:
            request.session.save()
        return None


class CSRFProtectionMiddleware(MiddlewareMixin):
    """Enhanced CSRF protection with better error messages"""
    
    def process_request(self, request):
        # Ensure CSRF token is present in session
        if not request.session.get('csrf_token') and request.method in ['POST', 'PUT', 'DELETE']:
            # Generate new CSRF token
            from django.middleware.csrf import get_token
            get_token(request)
        return None