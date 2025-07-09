# MyCoach - Coaching Sportif Intelligent 🏋️‍♂️

Application de coaching sportif avec adaptation intelligente des entraînements basée sur Django REST Framework.

## 🚀 Fonctionnalités Principales

### Intelligence Adaptative
- **Progression automatique** : Ajustement des charges selon la règle 3×12
- **Calculs 1RM** : Brzycki, Epley et formule adaptative personnalisée
- **IMC intelligent** : Interprétation avec recommandations d'entraînement
- **Temps de repos adaptatif** : Basé sur l'intensité et les objectifs

### Catalogue Complet
- **150+ machines** pré-configurées avec instructions détaillées
- **14 groupes musculaires** avec exercices ciblés
- **Instructions d'utilisation** et conseils de sécurité
- **Types variés** : cardio, musculation, poids libre, fonctionnel

### Planification Avancée
- **Templates d'entraînement** réutilisables
- **Planification récurrente** (quotidien, hebdomadaire, mensuel)
- **Import CSV** pour migration de données existantes
- **Calendrier intégré** avec gestion d'événements

### Suivi Performance
- **Records automatiques** : détection et historique
- **Statistiques détaillées** : volume, progression, tendances
- **RPE tracking** : échelle d'effort perçu
- **Graphiques d'évolution** des performances

## 🛠️ Stack Technique

- **Backend** : Django 4.2 + Django REST Framework
- **Base de données** : PostgreSQL
- **Authentification** : JWT avec SimpleJWT
- **Conteneurisation** : Docker + Docker Compose
- **Déploiement** : Railway (auto-build)
- **Cache** : Redis (optionnel)
- **Tâches async** : Celery

## 📦 Installation

### Prérequis
- Python 3.11+
- Docker et Docker Compose
- PostgreSQL (ou utiliser Docker)

### Installation Locale

1. **Cloner le repository**
```bash
git clone <repository-url>
cd mycoach
```

2. **Créer l'environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration environnement**
```bash
# Créer .env avec vos valeurs
cp .env.example .env
```

5. **Variables d'environnement (.env)**
```env
# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/mycoach

# Django
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# Redis (optionnel)
REDIS_URL=redis://localhost:6379/0
```

6. **Initialiser la base de données**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

7. **Charger les données initiales**
```bash
python seed_db.py
```

8. **Démarrer le serveur**
```bash
python manage.py runserver
```

### Installation avec Docker

1. **Démarrage complet avec Docker Compose**
```bash
# Construire et démarrer tous les services
docker-compose up --build

# En arrière-plan
docker-compose up -d --build
```

2. **Initialiser la base de données**
```bash
# Migrations
docker-compose exec web python manage.py migrate

# Créer superutilisateur
docker-compose exec web python manage.py createsuperuser

# Charger données initiales
docker-compose exec web python seed_db.py
```

3. **Services disponibles**
- **API** : http://localhost:8000
- **Admin** : http://localhost:8000/admin
- **PostgreSQL** : localhost:5432
- **Redis** : localhost:6379

## 🔑 API Endpoints

### Authentification
```bash
# Inscription
POST /api/auth/register/
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}

# Connexion
POST /api/auth/token/
{
  "email": "user@example.com",
  "password": "password123"
}

# Rafraîchir token
POST /api/auth/token/refresh/
{
  "refresh": "your-refresh-token"
}
```

### Profil Utilisateur
```bash
# Obtenir profil
GET /api/users/profile/
Authorization: Bearer your-access-token

# Mettre à jour profil
PUT /api/users/profile/
{
  "height_cm": 175,
  "weight_kg": 70,
  "objective": "muscle_gain",
  "level": "intermediate"
}
```

### Machines et Équipements
```bash
# Liste des machines
GET /api/machines/machines/

# Filtrer par type
GET /api/machines/machines/?machine_type=cardio

# Groupes musculaires
GET /api/machines/muscle-groups/
```

### Entraînements
```bash
# Créer séance
POST /api/workouts/workouts/
{
  "name": "Séance Pectoraux",
  "date": "2024-01-15T10:00:00Z",
  "planned_duration_minutes": 60
}

# Ajouter exercice
POST /api/workouts/exercises/
{
  "workout": 1,
  "machine": 5,
  "target_sets": 3,
  "target_reps": 12,
  "target_weight": 50.0
}

# Enregistrer série
POST /api/workouts/series/
{
  "exercise": 1,
  "set_number": 1,
  "reps": 12,
  "weight": 50.0,
  "rpe": 7,
  "completed": true
}
```

## 📊 Utilisation des Services Intelligents

### Service IMC
```python
from apps.core.services import IMCService

# Calcul et interprétation
imc = IMCService.calculate_imc(weight_kg=70, height_cm=175)
interpretation = IMCService.interpret_imc(imc, 25, 'male')
print(f"IMC: {imc}, Catégorie: {interpretation['category']}")
```

### Service 1RM
```python
from apps.core.services import OneRMService

# Différentes méthodes de calcul
brzycki = OneRMService.calculate_brzycki(weight=50, reps=10)
epley = OneRMService.calculate_epley(weight=50, reps=10)

# 1RM adaptatif basé sur le profil utilisateur
adaptive = OneRMService.calculate_adaptive_1rm(
    user=user, weight=50, reps=10, exercise_type='strength'
)
```

### Service de Progression
```python
from apps.core.services import ProgressionService

# Vérifier si augmenter le poids
should_increase = ProgressionService.should_increase_weight(
    target_reps=12, achieved_reps=[12, 11, 10], total_sets=3
)

# Calculer le prochain poids
next_weight = ProgressionService.calculate_next_weight(
    current_weight=50.0,
    success=True,
    objective='muscle_gain',
    exercise_type='strength'
)
```

## 🧪 Tests

```bash
# Tous les tests
python manage.py test

# Tests par application
python manage.py test apps.core
python manage.py test apps.workouts

# Avec coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Rapport HTML dans htmlcov/
```

## 📈 Monitoring et Logs

### Niveaux de logs configurés
- **DEBUG** : Développement seulement
- **INFO** : Opérations business importantes
- **WARNING** : Problèmes performance
- **ERROR** : Erreurs d'application
- **CRITICAL** : Erreurs système

### Logs disponibles
```bash
# Logs Django
tail -f logs/django.log

# Logs business (calculs, progressions)
tail -f logs/business.log

# Logs performance
tail -f logs/performance.log
```

## 🚀 Déploiement

### Railway (Recommandé)

1. **Connecter le repository** à Railway
2. **Configurer les variables d'environnement** :
   - `DATABASE_URL` (auto-configuré)
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `ALLOWED_HOSTS`
3. **Déploiement automatique** à chaque push

### Variables d'environnement Production
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-production-jwt-key
ALLOWED_HOSTS=mycoach-backend.railway.app
DATABASE_URL=postgresql://...  # Auto-configuré Railway
```

## 📱 Application Mobile (Future)

L'API est conçue pour supporter une application mobile Android avec :
- Authentification JWT
- Synchronisation offline/online
- Push notifications pour rappels
- Interface intuitive pour suivi d'entraînement

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

### Standards de Code
- PEP 8 pour Python
- Tests unitaires obligatoires pour nouvelle logique
- Documentation docstring pour fonctions publiques
- Type hints recommandés

## 📋 TODO / Roadmap

### Phase 1 (Actuel) ✅
- [x] Architecture Django complète
- [x] Modèles et API REST
- [x] Algorithmes intelligents (1RM, progression, IMC)
- [x] Catalogue machines complet
- [x] Système de planification
- [x] Interface admin avancée

### Phase 2 (Q2 2024)
- [ ] Application mobile Android
- [ ] Synchronisation données offline
- [ ] Push notifications
- [ ] Export/import données

### Phase 3 (Q3 2024)
- [ ] Machine Learning prédictif
- [ ] Recommandations IA
- [ ] Intégration capteurs IoT
- [ ] Social features

## 🐛 Support

- **Issues** : Utiliser GitHub Issues
- **Documentation API** : `/api/docs/` (Swagger UI)
- **Interface Admin** : `/admin/`
- **Email** : support@mycoach.com

## 📄 Licence

MIT License - Voir fichier [LICENSE](LICENSE)

---

**MyCoach** - Votre coach sportif intelligent 💪

*Développé avec ❤️ et Django*