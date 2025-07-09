#!/usr/bin/env python
"""
Script d'initialisation de la base de données MyCoach
Importe automatiquement les machines, groupes musculaires et labels de base
"""

import os
import django
import json
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycoach.settings')
django.setup()

from apps.machines.models import Machine, MuscleGroup, Label
from apps.users.models import User


def create_muscle_groups():
    """Créer les groupes musculaires de base"""
    muscle_groups_data = [
        # Haut du corps
        {
            'name': 'Pectoraux',
            'description': 'Muscles de la poitrine, incluant grand et petit pectoral',
            'anatomical_zone': 'upper_body'
        },
        {
            'name': 'Dos',
            'description': 'Muscles du dos, incluant dorsaux, rhomboïdes, trapèzes',
            'anatomical_zone': 'upper_body'
        },
        {
            'name': 'Biceps',
            'description': 'Muscles avant du bras',
            'anatomical_zone': 'upper_body'
        },
        {
            'name': 'Triceps',
            'description': 'Muscles arrière du bras',
            'anatomical_zone': 'upper_body'
        },
        {
            'name': 'Épaules',
            'description': 'Muscles deltoïdes et stabilisateurs',
            'anatomical_zone': 'upper_body'
        },
        {
            'name': 'Avant-bras',
            'description': 'Muscles de l\'avant-bras et préhension',
            'anatomical_zone': 'upper_body'
        },

        # Bas du corps
        {
            'name': 'Quadriceps',
            'description': 'Muscles avant de la cuisse',
            'anatomical_zone': 'lower_body'
        },
        {
            'name': 'Ischio-jambiers',
            'description': 'Muscles arrière de la cuisse',
            'anatomical_zone': 'lower_body'
        },
        {
            'name': 'Fessiers',
            'description': 'Muscles des fesses',
            'anatomical_zone': 'lower_body'
        },
        {
            'name': 'Mollets',
            'description': 'Muscles du mollet et soléaire',
            'anatomical_zone': 'lower_body'
        },
        {
            'name': 'Adducteurs',
            'description': 'Muscles intérieurs de la cuisse',
            'anatomical_zone': 'lower_body'
        },

        # Core
        {
            'name': 'Abdominaux',
            'description': 'Muscles abdominaux, grand droit, obliques',
            'anatomical_zone': 'core'
        },
        {
            'name': 'Lombaires',
            'description': 'Muscles du bas du dos',
            'anatomical_zone': 'core'
        },

        # Corps entier
        {
            'name': 'Cardio-respiratoire',
            'description': 'Système cardiovasculaire et respiratoire',
            'anatomical_zone': 'full_body'
        }
    ]

    created_groups = {}
    for group_data in muscle_groups_data:
        group, created = MuscleGroup.objects.get_or_create(
            name=group_data['name'],
            defaults=group_data
        )
        created_groups[group.name] = group
        if created:
            print(f"✓ Créé groupe musculaire: {group.name}")
        else:
            print(f"- Groupe musculaire existe déjà: {group.name}")

    return created_groups


def create_labels():
    """Créer les labels de base"""
    labels_data = [
        # Labels principaux
        {
            'name': 'Cardio',
            'description': 'Exercices cardiovasculaires',
            'color': '#e74c3c',
            'is_primary': True
        },
        {
            'name': 'Force',
            'description': 'Exercices de musculation/force',
            'color': '#3498db',
            'is_primary': True
        },
        {
            'name': 'Endurance',
            'description': 'Exercices d\'endurance musculaire',
            'color': '#f39c12',
            'is_primary': True
        },
        {
            'name': 'Flexibilité',
            'description': 'Exercices d\'étirement et mobilité',
            'color': '#9b59b6',
            'is_primary': True
        },

        # Labels secondaires
        {
            'name': 'Isolation',
            'description': 'Exercices mono-articulaires',
            'color': '#1abc9c',
            'is_primary': False
        },
        {
            'name': 'Compound',
            'description': 'Exercices poly-articulaires',
            'color': '#34495e',
            'is_primary': False
        },
        {
            'name': 'Machine',
            'description': 'Équipement machine guidée',
            'color': '#95a5a6',
            'is_primary': False
        },
        {
            'name': 'Poids libre',
            'description': 'Haltères, barres, kettlebells',
            'color': '#27ae60',
            'is_primary': False
        },
        {
            'name': 'Poids du corps',
            'description': 'Exercices au poids du corps',
            'color': '#e67e22',
            'is_primary': False
        },
        {
            'name': 'Fonctionnel',
            'description': 'Mouvements fonctionnels',
            'color': '#8e44ad',
            'is_primary': False
        }
    ]

    created_labels = {}
    for label_data in labels_data:
        label, created = Label.objects.get_or_create(
            name=label_data['name'],
            defaults=label_data
        )
        created_labels[label.name] = label
        if created:
            print(f"✓ Créé label: {label.name}")
        else:
            print(f"- Label existe déjà: {label.name}")

    return created_labels


def create_machines(muscle_groups, labels):
    """Créer les machines de base (type BasicFit)"""
    machines_data = [
        # MACHINES CARDIO
        {
            'name': 'Tapis de course',
            'brand': 'Life Fitness',
            'machine_type': 'cardio',
            'description': 'Tapis de course motorisé pour la course et la marche',
            'instructions': 'Montez sur le tapis, ajustez la vitesse progressivement. Utilisez les barres latérales pour l\'équilibre.',
            'safety_notes': 'Portez des chaussures adaptées. Ne sautez jamais du tapis en marche.',
            'difficulty_level': 1,
            'primary_muscles': ['Cardio-respiratoire', 'Quadriceps', 'Mollets'],
            'secondary_muscles': ['Ischio-jambiers', 'Fessiers'],
            'labels': ['Cardio', 'Endurance', 'Machine'],
            'supports_speed': True,
            'supports_incline': True,
            'supports_resistance': False,
            'gym_location': 'Zone Cardio'
        },
        {
            'name': 'Vélo elliptique',
            'brand': 'Life Fitness',
            'machine_type': 'cardio',
            'description': 'Appareil cardio à mouvement elliptique, faible impact',
            'instructions': 'Placez les pieds sur les pédales, saisissez les poignées et effectuez un mouvement fluide.',
            'safety_notes': 'Gardez le dos droit, ne lâchez pas les poignées pendant l\'exercice.',
            'difficulty_level': 1,
            'primary_muscles': ['Cardio-respiratoire', 'Quadriceps'],
            'secondary_muscles': ['Ischio-jambiers', 'Fessiers', 'Bras'],
            'labels': ['Cardio', 'Endurance', 'Machine'],
            'supports_speed': False,
            'supports_incline': False,
            'supports_resistance': True,
            'min_weight': 1,
            'max_weight': 25,
            'weight_increment': 1,
            'gym_location': 'Zone Cardio'
        },
        {
            'name': 'Vélo stationnaire',
            'brand': 'Life Fitness',
            'machine_type': 'cardio',
            'description': 'Vélo d\'appartement pour entraînement cardio assis',
            'instructions': 'Ajustez la selle à la hauteur des hanches, pédalez à rythme régulier.',
            'safety_notes': 'Vérifiez le serrage de la selle avant utilisation.',
            'difficulty_level': 1,
            'primary_muscles': ['Cardio-respiratoire', 'Quadriceps'],
            'secondary_muscles': ['Mollets', 'Fessiers'],
            'labels': ['Cardio', 'Endurance', 'Machine'],
            'supports_speed': False,
            'supports_incline': False,
            'supports_resistance': True,
            'min_weight': 1,
            'max_weight': 20,
            'weight_increment': 1,
            'gym_location': 'Zone Cardio'
        },

        # MACHINES DE MUSCULATION - HAUT DU CORPS
        {
            'name': 'Développé couché machine',
            'brand': 'Technogym',
            'machine_type': 'strength',
            'description': 'Machine guidée pour le développé couché, travail des pectoraux',
            'instructions': 'Allongez-vous sur le banc, saisissez les poignées, poussez en expirant.',
            'safety_notes': 'Gardez les pieds au sol, ne verrouillez pas complètement les coudes.',
            'difficulty_level': 2,
            'primary_muscles': ['Pectoraux'],
            'secondary_muscles': ['Triceps', 'Épaules'],
            'labels': ['Force', 'Compound', 'Machine'],
            'supports_speed': False,
            'supports_incline': False,
            'supports_resistance': True,
            'min_weight': 10,
            'max_weight': 200,
            'weight_increment': 5,
            'gym_location': 'Zone Musculation'
        },
        {
            'name': 'Tirage horizontal',
            'brand': 'Technogym',
            'machine_type': 'strength',
            'description': 'Machine pour tirage horizontal, développement du dos',
            'instructions': 'Assis, poitrine contre le support, tirez les poignées vers vous.',
            'safety_notes': 'Gardez le dos droit, ne donnez pas d\'à-coups.',
            'difficulty_level': 2,
            'primary_muscles': ['Dos'],
            'secondary_muscles': ['Biceps', 'Épaules'],
            'labels': ['Force', 'Compound', 'Machine'],
            'supports_speed': False,
            'supports_incline': False,
            'supports_resistance': True,
            'min_weight': 10,
            'max_weight': 150,
            'weight_increment': 5,
            'gym_location': 'Zone Musculation'
        },
        {
            'name': 'Lat Pulldown',
            'brand': 'Technogym',
            'machine_type': 'strength',
            'description': 'Machine pour tirage vertical, simulation des tractions',
            'instructions': 'Assis, saisissez la barre large, tirez vers la poitrine.',
            'safety_notes': 'Ne tirez pas derrière la nuque, contrôlez la remontée.',
            'difficulty_level': 2,
            'primary_muscles': ['Dos'],
            'secondary_muscles': ['Biceps', 'Épaules'],
            'labels': ['Force', 'Compound', 'Machine'],
            'supports_speed': False,
            'supports_incline': False,
            'supports_resistance': True,
            'min_weight': 10,
            'max_weight': 140,
            'weight_increment': 5,
            'gym_location': 'Zone Musculation'
        },
        {
            'name': 'Développé épaules machine',
            'brand': 'Technogym',
            'machine_type': 'strength',
            'description': 'Machine pour développé militaire assis',
            'instructions': 'Assis, dos contre le dossier, poussez vers le haut.',
            'safety_notes': 'Ne descendez pas trop bas, gardez les abdos contractés.',
            'difficulty_level': 2,
            'primary_muscles': ['Épaules'],
            'secondary_muscles': ['Triceps'],
            'labels': ['Force', 'Compound', 'Machine'],
            'supports_speed': False,
            'supports_incline': False,
            'supports_resistance': True,
            'min_weight': 5,
            'max_weight': 100,
            'weight_increment': 2.5,
            'gym_location': 'Zone Musculation'
        },

        # MACHINES BAS DU CORPS
        {
            'name': 'Leg Press',
            'brand': 'Technogym',
            'machine_type': 'strength',
            'description': 'Machine pour presse à cuisses, développement des jambes',
            'instructions': 'Allongé, pieds sur la plateforme, poussez avec les jambes.',
            'safety_notes': 'Ne verrouillez pas les genoux, gardez les pieds parallèles.',
            'difficulty_level': 2,
            'primary_muscles': ['Quadriceps', 'Fessiers'],
            'secondary_muscles': ['Ischio-jambiers', 'Mollets'],
            'labels': ['Force', 'Compound', 'Machine'],
            'supports_speed': False,
            'supports_incline': False,
            'supports_resistance': True,
            'min_weight': 20,
            'max_weight': 400,
            'weight_increment': 10,
            'gym_location': 'Zone Musculation'
        },
        {
            'name': 'Leg Extension',
            'brand': 'Technogym',
            'machine_type': 'strength',
            'description': 'Machine d\'extension des jambes, isolation des quadriceps',
            'instructions': 'Assis, chevilles sous les boudins, étendez les jambes.',
            'safety_notes': 'Mouvement contrôlé, ne clacquez pas les genoux.',
            'difficulty_level': 1,
            'primary_muscles': ['Quadriceps'],
            'secondary_muscles': [],
            'labels': ['Force', 'Isolation', 'Machine'],
            'supports_speed': False,
            'supports_incline': False,
            'supports_resistance': True,
            'min_weight': 5,
            'max_weight': 120,
            'weight_increment': 5,
            'gym_location': 'Zone Musculation'
        },
        {
            'name': 'Leg Curl',
            'brand': 'Technogym',
            'machine_type': 'strength',
            'description': 'Machine pour flexion des jambes, isolation des ischio-jambiers',
            'instructions': 'Allongé face vers le bas, fléchissez les jambes vers les fesses.',
            'safety_notes': 'Ne donnez pas de coups, mouvement fluide.',
            'difficulty_level': 1,
            'primary_muscles': ['Ischio-jambiers'],
            'secondary_muscles': ['Mollets'],
            'labels': ['Force', 'Isolation', 'Machine'],
            'supports_speed': False,
            'supports_incline': False,
            'supports_resistance': True,
            'min_weight': 5,
            'max_weight': 100,
            'weight_increment': 5,
            'gym_location': 'Zone Musculation'
        },

        # POIDS LIBRES
        {
            'name': 'Haltères',
            'brand': 'Various',
            'machine_type': 'free_weights',
            'description': 'Set d\'haltères de 1kg à 50kg pour exercices libres',
            'instructions': 'Sélectionnez le poids approprié, maintenez une forme correcte.',
            'safety_notes': 'Toujours remettre en place, vérifier l\'équilibre.',
            'difficulty_level': 3,
            'primary_muscles': ['Corps entier'],
            'secondary_muscles': [],
            'labels': ['Force', 'Poids libre', 'Compound'],
            'supports_speed': False,
            'supports_incline': False,
            'supports_resistance': True,
            'min_weight': 1,
            'max_weight': 50,
            'weight_increment': 1,
            'gym_location': 'Zone Poids Libres'
        },
        {
            'name': 'Barre de musculation',
            'brand': 'Olympic',
            'machine_type': 'free_weights',
            'description': 'Barre olympique 20kg pour exercices composés',
            'instructions': 'Utilisez avec des disques, toujours avec un partenaire pour les gros poids.',
            'safety_notes': 'Utilisez des colliers de serrage, respectez les zones de sécurité.',
            'difficulty_level': 4,
            'primary_muscles': ['Corps entier'],
            'secondary_muscles': [],
            'labels': ['Force', 'Poids libre', 'Compound'],
            'supports_speed': False,
            'supports_incline': False,
            'supports_resistance': True,
            'min_weight': 20,
            'max_weight': 200,
            'weight_increment': 1.25,
            'gym_location': 'Zone Poids Libres'
        },

        # EXERCICES FONCTIONNELS
        {
            'name': 'TRX',
            'brand': 'TRX',
            'machine_type': 'bodyweight',
            'description': 'Système de suspension pour entraînement au poids du corps',
            'instructions': 'Ajustez la longueur selon l\'exercice, utilisez votre poids corporel.',
            'safety_notes': 'Vérifiez l\'ancrage, progression graduelle.',
            'difficulty_level': 3,
            'primary_muscles': ['Corps entier'],
            'secondary_muscles': [],
            'labels': ['Fonctionnel', 'Poids du corps', 'Compound'],
            'supports_speed': False,
            'supports_incline': False,
            'supports_resistance': False,
            'gym_location': 'Zone Fonctionnelle'
        }
    ]

    created_machines = []
    for machine_data in machines_data:
        # Récupérer les objets muscle groups
        primary_muscle_objects = []
        for muscle_name in machine_data.pop('primary_muscles', []):
            if muscle_name in muscle_groups:
                primary_muscle_objects.append(muscle_groups[muscle_name])

        secondary_muscle_objects = []
        for muscle_name in machine_data.pop('secondary_muscles', []):
            if muscle_name in muscle_groups:
                secondary_muscle_objects.append(muscle_groups[muscle_name])

        # Récupérer les objets labels
        label_objects = []
        for label_name in machine_data.pop('labels', []):
            if label_name in labels:
                label_objects.append(labels[label_name])

        # Créer ou récupérer la machine
        machine, created = Machine.objects.get_or_create(
            name=machine_data['name'],
            defaults=machine_data
        )

        if created:
            # Ajouter les relations many-to-many
            machine.primary_muscles.set(primary_muscle_objects)
            machine.secondary_muscles.set(secondary_muscle_objects)
            machine.labels.set(label_objects)
            created_machines.append(machine)
            print(f"✓ Créée machine: {machine.name}")
        else:
            print(f"- Machine existe déjà: {machine.name}")

    return created_machines


def create_admin_user():
    """Créer un utilisateur admin par défaut si aucun superuser n'existe"""
    if not User.objects.filter(is_superuser=True).exists():
        admin_user = User.objects.create_superuser(
            email='admin@mycoach.com',
            first_name='Admin',
            last_name='MyCoach',
            password='admin123'
        )
        print(f"✓ Créé utilisateur admin: {admin_user.email}")
        print("  Email: admin@mycoach.com")
        print("  Mot de passe: admin123")
        return admin_user
    else:
        print("- Un superuser existe déjà")
        return None


def main():
    """Fonction principale d'initialisation"""
    print("🚀 Initialisation de la base de données MyCoach")
    print("=" * 50)

    try:
        # Créer les groupes musculaires
        print("\n📊 Création des groupes musculaires...")
        muscle_groups = create_muscle_groups()

        # Créer les labels
        print("\n🏷️  Création des labels...")
        labels = create_labels()

        # Créer les machines
        print("\n🏋️  Création des machines...")
        machines = create_machines(muscle_groups, labels)

        # Créer l'utilisateur admin
        print("\n👤 Création de l'utilisateur admin...")
        admin_user = create_admin_user()

        print("\n" + "=" * 50)
        print("✅ Initialisation terminée avec succès!")
        print(f"📊 {len(muscle_groups)} groupes musculaires")
        print(f"🏷️  {len(labels)} labels")
        print(f"🏋️  {len(machines)} nouvelles machines")
        if admin_user:
            print("👤 1 utilisateur admin créé")

        print("\n🌐 Vous pouvez maintenant:")
        print("  - Accéder à l'admin Django: /admin/")
        print("  - Utiliser l'API REST: /api/")
        print("  - Tester les endpoints avec les données créées")

    except Exception as e:
        print(f"\n❌ Erreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)