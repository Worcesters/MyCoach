# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
import os

# Ne pas importer celery pendant la collecte des fichiers statiques
if not os.environ.get('DJANGO_COLLECTSTATIC'):
    try:
        from .celery import app as celery_app
        __all__ = ('celery_app',)
    except ImportError:
        # Celery pas disponible, ignorer
        __all__ = ()
else:
    __all__ = ()