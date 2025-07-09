from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.csrf import csrf_exempt

class DisableCSRFMiddleware(MiddlewareMixin):
    """
    Middleware pour désactiver la protection CSRF sur les URLs d'API.
    Utilisé pour les API REST avec authentification JWT.
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Désactiver CSRF pour toutes les URLs commençant par /api/
        if request.path.startswith('/api/'):
            setattr(view_func, 'csrf_exempt', True)
        return None