# Architecture MyCoach - Documentation Technique

## Vue d'ensemble du projet

MyCoach est une application de coaching sportif intelligent développée avec Django REST Framework pour le backend et préparée pour une application mobile Android. Le système utilise des algorithmes intelligents pour adapter automatiquement les entraînements en fonction des performances et de l'historique de l'utilisateur.

## Stack Technologique

### Backend
- **Framework**: Django 4.2 + Django REST Framework
- **Base de données**: PostgreSQL
- **Authentification**: SimpleJWT (JSON Web Tokens)
- **Cache**: Redis (optionnel)
- **Tâches asynchrones**: Celery
- **Conteneurisation**: Docker + Docker Compose
- **Déploiement**: Railway (auto-build)

### Frontend Mobile (prévu)
- **Plateforme**: Android natif
- **Communication**: API REST avec authentification JWT

## Architecture du Projet

```
mycoach/
├── mycoach/                 # Configuration Django principale
│   ├── __init__.py
│   ├── settings.py         # Configuration avec env variables
│   ├── urls.py             # URLs principales
│   ├── wsgi.py            # Configuration WSGI
│   ├── asgi.py            # Configuration ASGI
│   └── celery.py          # Configuration Celery
│
├── apps/                   # Applications Django
│   ├── core/              # Services métier et utilitaires
│   ├── users/             # Gestion des utilisateurs
│   ├── machines/          # Équipements sportifs
│   ├── workouts/          # Séances d'entraînement
│   └── calendar/          # Planification et calendrier
│
├── static/                # Fichiers statiques
├── media/                 # Fichiers uploadés
├── requirements.txt       # Dépendances Python
├── Dockerfile            # Image Docker
├── docker-compose.yml    # Orchestration Docker
├── entrypoint.sh         # Script de démarrage
├── manage.py             # Commandes Django
└── seed_db.py            # Script d'initialisation des données
```

## Applications Django

### 1. Core (`apps.core`)
Services métier centralisés et logique algorithmique.

**Responsabilités:**
- Services de calcul IMC avec interprétation
- Algorithmes de calcul 1RM (Brzycki, Epley, adaptatif)
- Logique de progression automatique des charges
- Services de statistiques et tendances
- Utilitaires communs

**Modèles:** Aucun (services purs)

**Services principaux:**
- `IMCService`: Calcul et interprétation de l'IMC
- `OneRMService`: Calculs de 1RM multiples méthodes
- `ProgressionService`: Progression intelligente des charges
- `StatisticsService`: Analyses et statistiques

### 2. Users (`apps.users`)
Gestion des utilisateurs avec extension du modèle Django.

**Modèles:**
- `User`: Extension du modèle Django avec profil sportif complet
  - Informations personnelles (âge, sexe, morphologie)
  - Objectifs d'entraînement et niveau
  - Préférences et historique
  - Calculs automatiques (IMC, 1RM adaptatif)

**Fonctionnalités:**
- Authentification JWT
- Profils utilisateur étendus
- Calculs de performances personnalisés
- Gestion des préférences

### 3. Machines (`apps.machines`)
Catalogue complet des équipements sportifs.

**Modèles:**
- `MuscleGroup`: Groupes musculaires (14 principaux)
- `Label`: Étiquettes pour catégorisation
- `Machine`: Équipements avec descriptions complètes
  - Types multiples (cardio, musculation, poids libre)
  - Instructions d'utilisation détaillées
  - Relations avec groupes musculaires
  - Conseils et images

**Données fournies:**
- 150+ machines pré-configurées
- Instructions d'utilisation complètes
- Groupes musculaires ciblés
- Conseils de sécurité

### 4. Workouts (`apps.workouts`)
Gestion des séances d'entraînement avec intelligence adaptative.

**Modèles principaux:**
- `WorkoutTemplate`: Templates de séances réutilisables
- `Workout`: Séances d'entraînement avec suivi complet
- `Exercise`: Exercices dans une séance avec progression
- `Serie`: Séries individuelles avec métriques détaillées
- `PerformanceRecord`: Records et performances historiques
- `WorkoutProgram`: Programmes d'entraînement structurés

**Intelligence intégrée:**
- Progression automatique selon la règle 3×12
- Calcul adaptatif des poids suggérés
- Suivi des RPE (Rate of Perceived Exertion)
- Détection automatique des records
- Analyse des tendances de performance

### 5. Calendar (`apps.calendar`)
Planification intelligente et gestion du calendrier.

**Modèles:**
- `WorkoutPlan`: Planification des séances avec récurrence
- `CalendarEvent`: Événements du calendrier (séances, repos, notes)
- `WeeklyTemplate`: Templates hebdomadaires d'entraînement
- `CSVImport`: Import de données CSV avec validation

**Fonctionnalités:**
- Planification récurrente (quotidien, hebdomadaire, mensuel)
- Templates de semaine configurables
- Import CSV de données d'entraînement
- Notifications et rappels
- Gestion des événements multiples

## Algorithmes Intelligents

### 1. Calcul du 1RM (One Rep Max)
Trois méthodes implémentées:

**Brzycki:** `1RM = poids / (1.0278 - 0.0278 × répétitions)`
**Epley:** `1RM = poids × (1 + répétitions/30)`
**Adaptatif:** Formule personnalisée basée sur l'âge, l'objectif et l'historique

### 2. Progression Automatique
Système intelligent d'adaptation des charges:

```python
# Règle 3×12: Si toutes les séries atteignent les répétitions cibles
if all_sets_completed_successfully:
    increase_weight_by_percentage()

# Adaptation selon l'objectif
- Force: +2.5-5kg, moins de répétitions
- Hypertrophie: +1.25-2.5kg, répétitions modérées
- Endurance: Maintien poids, plus de répétitions
```

### 3. Calcul IMC et Interprétation
Classification WHO avec recommandations personnalisées:
- Sous-poids (<18.5): Programmes de prise de masse
- Normal (18.5-24.9): Programmes équilibrés
- Surpoids (25-29.9): Programmes cardio-force
- Obésité (≥30): Programmes axés cardio

### 4. Temps de Repos Adaptatif
Calcul basé sur l'intensité et l'objectif:
```python
base_rest = 90  # secondes
if weight_percentage > 85:  # Charges lourdes
    rest_time = base_rest * 1.5
elif rpe >= 8:  # Effort élevé
    rest_time = base_rest * 1.3
```

## Base de Données

### Schéma Principal

```sql
-- Utilisateurs avec profil étendu
users_user (
    id, email, password, first_name, last_name,
    birth_date, sex, height_cm, weight_kg,
    objective, level, last_workout_date
)

-- Équipements sportifs
machines_musclegroup (id, name, description)
machines_label (id, name, color)
machines_machine (
    id, name, machine_type, description,
    instructions, tips, image_url
)

-- Entraînements
workouts_workout (
    id, user_id, name, date, status,
    planned_duration, actual_duration,
    difficulty_felt, satisfaction
)

workouts_exercise (
    id, workout_id, machine_id, order,
    target_sets, target_reps, target_weight,
    auto_progression
)

workouts_serie (
    id, exercise_id, set_number,
    reps, weight, rpe, completed
)

-- Planification
calendar_workoutplan (
    id, user_id, template_id, title,
    scheduled_date, repeat_type, is_active
)
```

### Relations Clés
- `User` → `Workout` (1:N)
- `Workout` → `Exercise` (1:N)
- `Exercise` → `Serie` (1:N)
- `Machine` → `MuscleGroup` (N:N)
- `WorkoutTemplate` → `WorkoutPlan` (1:N)

## API REST

### Authentification
```
POST /api/auth/token/        # Obtenir token JWT
POST /api/auth/token/refresh/ # Rafraîchir token
POST /api/auth/register/     # Inscription
```

### Endpoints Principaux
```
# Utilisateurs
GET/PUT /api/users/profile/

# Machines
GET /api/machines/machines/
GET /api/machines/muscle-groups/

# Entraînements
GET/POST /api/workouts/workouts/
GET/POST /api/workouts/exercises/
POST /api/workouts/start-workout/
POST /api/workouts/complete-workout/

# Calendrier
GET/POST /api/calendar/plans/
GET /api/calendar/events/
POST /api/calendar/import-csv/
```

## Sécurité

### Authentification JWT
- Tokens avec expiration courte (15 min)
- Refresh tokens longue durée (7 jours)
- Révocation possible côté serveur

### Permissions
- Accès basé sur l'utilisateur authentifié
- Isolation complète des données par utilisateur
- Validation stricte des entrées

### Protection CORS
Configuration pour application mobile:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Dev
    "https://mycoach-app.com"  # Prod
]
```

## Performance

### Optimisations Base de Données
- Index sur champs fréquemment interrogés
- `select_related` et `prefetch_related` pour éviter N+1
- Pagination sur toutes les listes

### Cache Strategy
```python
# Cache des machines (données statiques)
@cache_page(3600)  # 1 heure

# Cache des statistiques utilisateur
@cache_page(300)   # 5 minutes
```

### Monitoring
- Logs structurés avec niveaux
- Métriques de performance API
- Alertes sur erreurs critiques

## Déploiement

### Docker
```dockerfile
# Image Python 3.11 slim
FROM python:3.11-slim

# Installation des dépendances
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copie du code
COPY . /app
WORKDIR /app

# Script d'entrée
ENTRYPOINT ["./entrypoint.sh"]
```

### Railway Configuration
- Auto-build depuis le repository Git
- Variables d'environnement sécurisées
- Base PostgreSQL managed
- Scaling automatique

### Variables d'Environnement
```env
# Base de données
DATABASE_URL=postgresql://...

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=mycoach-backend.railway.app

# JWT
JWT_SECRET_KEY=jwt-secret

# Cache Redis (optionnel)
REDIS_URL=redis://...
```

## Tests

### Structure de Tests
```
apps/
├── core/tests/
│   ├── test_services.py
│   └── test_calculations.py
├── users/tests/
│   └── test_models.py
├── workouts/tests/
│   ├── test_models.py
│   ├── test_progression.py
│   └── test_api.py
```

### Tests d'Algorithmes
- Tests unitaires pour tous les calculs (1RM, IMC, progression)
- Tests de régression sur les algorithmes d'adaptation
- Tests de performance sur large datasets

## Monitoring et Logs

### Structure des Logs
```python
LOGGING = {
    'loggers': {
        'mycoach.business': {  # Logique métier
            'level': 'INFO',
        },
        'mycoach.performance': {  # Performances
            'level': 'WARNING',
        },
        'mycoach.security': {  # Sécurité
            'level': 'WARNING',
        }
    }
}
```

### Métriques Clés
- Temps de réponse API par endpoint
- Taux d'erreur par application
- Utilisation des algorithmes de progression
- Engagement utilisateur (séances complétées)

## Évolutions Futures

### Phase 2 - IA Avancée
- Machine Learning pour prédiction de performances
- Recommandations personnalisées d'exercices
- Détection d'anomalies dans les performances

### Phase 3 - Social
- Partage de programmes d'entraînement
- Challenges entre utilisateurs
- Coaching communautaire

### Phase 4 - IoT
- Intégration capteurs de fréquence cardiaque
- Synchronisation avec balances connectées
- API pour équipements de gym connectés

## Contact et Support

Pour questions techniques ou contributions:
- Architecture: Voir ce document
- Issues: GitHub repository
- API Documentation: `/api/docs/` (Swagger)
- Admin Interface: `/admin/`

---

*Documentation générée automatiquement - MyCoach v1.0*