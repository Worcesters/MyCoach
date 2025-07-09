# Guide de Déploiement MyCoach 🚀

## Déploiement Local (Développement)

### 1. Installation des Dépendances
```bash
# Créer environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Installer dépendances
pip install -r requirements.txt
```

### 2. Configuration Base de Données
```bash
# Variables d'environnement (copier .env.example vers .env)
cp .env.example .env

# Modifications dans .env
DATABASE_URL=sqlite:///db.sqlite3  # Pour développement simple
# ou
DATABASE_URL=postgresql://user:password@localhost:5432/mycoach
```

### 3. Initialisation
```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer migrations
python manage.py migrate

# Créer superutilisateur
python manage.py createsuperuser

# Charger données initiales (150+ machines)
python seed_db.py

# Démarrer serveur
python manage.py runserver
```

## Déploiement Docker (Local)

### 1. Avec Docker Compose
```bash
# Démarrer tous les services
docker-compose up --build

# En arrière-plan
docker-compose up -d --build
```

### 2. Initialiser la base
```bash
# Migrations
docker-compose exec web python manage.py migrate

# Superutilisateur
docker-compose exec web python manage.py createsuperuser

# Données initiales
docker-compose exec web python seed_db.py
```

### 3. Services Disponibles
- **API**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Déploiement Railway (Production)

### 1. Préparation
1. **Push du code** vers GitHub/GitLab
2. **Connecter Railway** au repository
3. **Railway détecte automatiquement** Django

### 2. Configuration Variables
Dans Railway Dashboard > Variables:
```env
SECRET_KEY=your-production-secret-key-here
JWT_SECRET_KEY=your-production-jwt-secret-key
DEBUG=False
ALLOWED_HOSTS=mycoach-backend.railway.app
```

### 3. Base de Données
1. **Ajouter PostgreSQL** service dans Railway
2. **DATABASE_URL** sera auto-configuré
3. **Pas de configuration manuelle** nécessaire

### 4. Déploiement Automatique
- **Push vers main/master** → Déploiement automatique
- **Build time**: ~5-10 minutes
- **Zero-downtime deployments**

### 5. Post-Déploiement
```bash
# Depuis Railway CLI ou dashboard
railway run python manage.py migrate
railway run python seed_db.py
```

## Déploiement Heroku (Alternative)

### 1. Prérequis
```bash
# Installer Heroku CLI
# Créer app Heroku
heroku create mycoach-backend
```

### 2. Configuration
```bash
# Variables d'environnement
heroku config:set SECRET_KEY=your-secret-key
heroku config:set JWT_SECRET_KEY=your-jwt-secret-key
heroku config:set DEBUG=False

# PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev
```

### 3. Déploiement
```bash
# Push vers Heroku
git push heroku main

# Migrations
heroku run python manage.py migrate

# Données initiales
heroku run python seed_db.py

# Créer superutilisateur
heroku run python manage.py createsuperuser
```

## Monitoring et Maintenance

### 1. Logs
```bash
# Railway
railway logs

# Heroku
heroku logs --tail

# Docker
docker-compose logs web
```

### 2. Base de Données
```bash
# Backup PostgreSQL
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

### 3. Mise à Jour
```bash
# 1. Nouvelles migrations
python manage.py makemigrations
python manage.py migrate

# 2. Nouveaux requirements
pip freeze > requirements.txt

# 3. Push et déploiement automatique
git add .
git commit -m "Update: nouvelles fonctionnalités"
git push origin main
```

## Sécurité Production

### 1. Variables Sensibles
- ✅ **SECRET_KEY**: Unique et complexe
- ✅ **JWT_SECRET_KEY**: Différent de SECRET_KEY
- ✅ **DATABASE_URL**: Chiffré si possible
- ❌ **DEBUG=False** en production

### 2. HTTPS
```python
# Dans settings.py pour production
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

### 3. CORS
```python
# Uniquement les domaines autorisés
CORS_ALLOWED_ORIGINS = [
    "https://mycoach-app.com",
    "https://www.mycoach-app.com",
]
```

## Performance

### 1. Cache Redis
```bash
# Ajouter Redis addon/service
# Railway: Add Redis service
# Heroku: heroku addons:create heroku-redis:hobby-dev
```

### 2. Static Files
```python
# Whitenoise configuré pour servir les fichiers statiques
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 3. Database Optimizations
```bash
# Index sur champs fréquents (déjà inclus dans models)
# Connexion pooling (django-environ configuré)
```

## Troubleshooting

### 1. Erreurs Communes
```bash
# Migration conflicts
python manage.py migrate --fake-initial

# Static files manquants
python manage.py collectstatic --noinput

# Permissions admin
python manage.py createsuperuser
```

### 2. Debug Mode
```python
# Activer temporairement en production (DANGER)
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### 3. Logs Détaillés
```python
# Dans settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## URLs Importantes

### Développement
- **API**: http://localhost:8000/api/
- **Admin**: http://localhost:8000/admin/
- **Swagger**: http://localhost:8000/api/docs/

### Production
- **API**: https://mycoach-backend.railway.app/api/
- **Admin**: https://mycoach-backend.railway.app/admin/
- **Swagger**: https://mycoach-backend.railway.app/api/docs/

---

✅ **Projet prêt pour le déploiement !**