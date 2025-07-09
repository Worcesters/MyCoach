#!/bin/bash

# Script d'entrée pour l'application MyCoach
set -e

echo "🚀 Démarrage de MyCoach..."

# Fonction pour attendre PostgreSQL
wait_for_postgres() {
    echo "⏳ Attente de PostgreSQL..."

    # Extraire les informations de connexion depuis DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | cut -d'@' -f2 | cut -d':' -f1)
    DB_PORT=$(echo $DATABASE_URL | cut -d'@' -f2 | cut -d':' -f2 | cut -d'/' -f1)

    # Si pas de port spécifié, utiliser 5432 par défaut
    if [ "$DB_PORT" = "$DB_HOST" ]; then
        DB_PORT="5432"
    fi

    echo "📡 Vérification de la connexion à $DB_HOST:$DB_PORT..."

    until nc -z "$DB_HOST" "$DB_PORT"; do
        echo "⏳ PostgreSQL n'est pas encore prêt - attente..."
        sleep 2
    done

    echo "✅ PostgreSQL est prêt!"
}

# Fonction pour attendre Redis
wait_for_redis() {
    if [ ! -z "$REDIS_URL" ]; then
        echo "⏳ Attente de Redis..."

        REDIS_HOST=$(echo $REDIS_URL | cut -d'/' -f3 | cut -d':' -f1)
        REDIS_PORT=$(echo $REDIS_URL | cut -d'/' -f3 | cut -d':' -f2)

        # Si pas de port spécifié, utiliser 6379 par défaut
        if [ "$REDIS_PORT" = "$REDIS_HOST" ]; then
            REDIS_PORT="6379"
        fi

        echo "📡 Vérification de la connexion à Redis $REDIS_HOST:$REDIS_PORT..."

        until nc -z "$REDIS_HOST" "$REDIS_PORT"; do
            echo "⏳ Redis n'est pas encore prêt - attente..."
            sleep 2
        done

        echo "✅ Redis est prêt!"
    fi
}

# Fonction pour exécuter les migrations
run_migrations() {
    if [ "$SKIP_MIGRATIONS" = "true" ]; then
        echo "⏭️ Migrations ignorées (SKIP_MIGRATIONS=true)"
        return 0
    fi

    echo "🔄 Exécution des migrations Django..."
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
    echo "✅ Migrations terminées!"
}

# Fonction pour collecter les fichiers statiques
collect_static() {
    echo "📦 Collecte des fichiers statiques..."
    python manage.py collectstatic --noinput --clear
    echo "✅ Fichiers statiques collectés!"
}

# Fonction pour initialiser les données
seed_database() {
    echo "🌱 Initialisation des données de base..."

    # Vérifier si des données existent déjà
    MACHINES_COUNT=$(python manage.py shell -c "from apps.machines.models import Machine; print(Machine.objects.count())")

    if [ "$MACHINES_COUNT" = "0" ]; then
        echo "📊 Aucune donnée trouvée, initialisation en cours..."
        python seed_db.py
        echo "✅ Données initialisées!"
    else
        echo "📊 Données déjà présentes ($MACHINES_COUNT machines), initialisation ignorée."
    fi
}

# Fonction pour créer un superuser si nécessaire
create_superuser() {
    echo "👤 Vérification de l'utilisateur admin..."

    SUPERUSER_EXISTS=$(python manage.py shell -c "from apps.users.models import User; print(User.objects.filter(is_superuser=True).exists())")

    if [ "$SUPERUSER_EXISTS" = "False" ]; then
        echo "👤 Création de l'utilisateur admin..."

        # Utiliser les variables d'environnement ou des valeurs par défaut
        ADMIN_EMAIL=${ADMIN_EMAIL:-admin@mycoach.com}
        ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin123}
        ADMIN_FIRST_NAME=${ADMIN_FIRST_NAME:-Admin}
        ADMIN_LAST_NAME=${ADMIN_LAST_NAME:-MyCoach}

        python manage.py shell -c "
from apps.users.models import User
try:
    user = User.objects.create_superuser(
        email='$ADMIN_EMAIL',
        password='$ADMIN_PASSWORD',
        first_name='$ADMIN_FIRST_NAME',
        last_name='$ADMIN_LAST_NAME'
    )
    print('✅ Superuser créé: $ADMIN_EMAIL')
except Exception as e:
    print(f'⚠️ Erreur création superuser: {e}')
    # Méthode alternative
    user = User(
        email='$ADMIN_EMAIL',
        first_name='$ADMIN_FIRST_NAME',
        last_name='$ADMIN_LAST_NAME',
        is_staff=True,
        is_superuser=True,
        is_active=True
    )
    user.set_password('$ADMIN_PASSWORD')
    user.save()
    print('✅ Superuser créé (méthode alternative): $ADMIN_EMAIL')
"
    else
        echo "👤 Un superuser existe déjà."
    fi
}

# Fonction principale
main() {
    # Si c'est une commande spéciale (comme pour Celery), l'exécuter directement
    if [ "$1" = "celery" ]; then
        echo "🔄 Démarrage de Celery: $@"
        wait_for_postgres
        wait_for_redis
        exec "$@"
    fi

    # Attendre les services
    wait_for_postgres
    wait_for_redis

    # Préparer l'application
    run_migrations
    collect_static

    # Initialiser les données seulement pour le service web principal
    if [ "$1" = "gunicorn" ] || [ -z "$1" ]; then
        seed_database
        create_superuser

        echo ""
        echo "🎉 MyCoach est prêt!"
        echo "📧 Admin: ${ADMIN_EMAIL:-admin@mycoach.com}"
        echo "🔑 Password: ${ADMIN_PASSWORD:-admin123}"
        echo "🌐 API: http://localhost:8000/api/"
        echo "⚙️  Admin: http://localhost:8000/admin/"
        echo ""
    fi

    # Exécuter la commande finale
    if [ -z "$1" ]; then
        echo "🚀 Démarrage du serveur Django..."
        exec gunicorn --bind 0.0.0.0:8000 --workers 3 mycoach.wsgi:application
    else
        echo "🚀 Exécution de: $@"
        exec "$@"
    fi
}

# Point d'entrée
main "$@"