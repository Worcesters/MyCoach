"""
Services métier pour l'application MyCoach
Contient les calculs et la logique d'entraînement intelligente
"""

import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum


class ObjectiveType(Enum):
    """Types d'objectifs d'entraînement"""
    MUSCLE_GAIN = "muscle_gain"
    WEIGHT_LOSS = "weight_loss"
    MAINTENANCE = "maintenance"


class IMCService:
    """Service pour le calcul et l'interprétation de l'IMC"""

    @staticmethod
    def calculate_imc(weight: float, height: float) -> float:
        """
        Calcule l'IMC (Indice de Masse Corporelle)

        Args:
            weight: Poids en kg
            height: Taille en cm

        Returns:
            IMC calculé
        """
        if height <= 0 or weight <= 0:
            raise ValueError("Le poids et la taille doivent être positifs")

        height_m = height / 100  # Conversion cm vers m
        return round(weight / (height_m ** 2), 2)

    @staticmethod
    def interpret_imc(imc: float) -> str:
        """
        Interprète la valeur de l'IMC

        Args:
            imc: Valeur de l'IMC

        Returns:
            Interprétation textuelle de l'IMC
        """
        if imc < 16.5:
            return "Dénutrition ou famine"
        elif imc < 18.5:
            return "Maigreur"
        elif imc < 25:
            return "Corpulence normale"
        elif imc < 30:
            return "Surpoids"
        elif imc < 35:
            return "Obésité modérée"
        elif imc < 40:
            return "Obésité sévère"
        else:
            return "Obésité morbide"


class OneRMService:
    """Service pour le calcul du 1RM (One Rep Max)"""

    @staticmethod
    def calculate_brzycki(weight: float, reps: int) -> float:
        """
        Calcule le 1RM selon la formule de Brzycki

        Args:
            weight: Poids soulevé
            reps: Nombre de répétitions effectuées

        Returns:
            1RM estimé
        """
        if reps <= 0 or weight <= 0:
            raise ValueError("Le poids et les répétitions doivent être positifs")

        if reps == 1:
            return weight

        return round(weight / (1.0278 - (0.0278 * reps)), 2)

    @staticmethod
    def calculate_epley(weight: float, reps: int) -> float:
        """
        Calcule le 1RM selon la formule d'Epley

        Args:
            weight: Poids soulevé
            reps: Nombre de répétitions effectuées

        Returns:
            1RM estimé
        """
        if reps <= 0 or weight <= 0:
            raise ValueError("Le poids et les répétitions doivent être positifs")

        if reps == 1:
            return weight

        return round(weight * (1 + (reps / 30)), 2)

    @staticmethod
    def calculate_adaptive_1rm(
        weight: float,
        reps: int,
        user_age: int,
        objective: ObjectiveType
    ) -> float:
        """
        Calcule le 1RM adapté selon l'âge et l'objectif

        Args:
            weight: Poids soulevé
            reps: Nombre de répétitions
            user_age: Âge de l'utilisateur
            objective: Objectif d'entraînement

        Returns:
            1RM adapté
        """
        # Calcul de base avec Brzycki
        base_1rm = OneRMService.calculate_brzycki(weight, reps)

        # Facteur d'âge (diminution progressive après 30 ans)
        age_factor = 1.0
        if user_age > 30:
            age_factor = 1 - ((user_age - 30) * 0.005)  # -0.5% par année après 30 ans

        # Facteur d'objectif
        objective_factors = {
            ObjectiveType.MUSCLE_GAIN: 1.05,    # +5% pour prise de masse
            ObjectiveType.WEIGHT_LOSS: 0.95,    # -5% pour sèche
            ObjectiveType.MAINTENANCE: 1.0      # Neutre
        }

        objective_factor = objective_factors.get(objective, 1.0)

        return round(base_1rm * age_factor * objective_factor, 2)


class ProgressionService:
    """Service pour gérer la progression intelligente des entraînements"""

    @staticmethod
    def should_increase_weight(
        target_reps: int,
        achieved_reps: List[int],
        target_sets: int
    ) -> bool:
        """
        Détermine s'il faut augmenter la charge

        Args:
            target_reps: Nombre de répétitions cible
            achieved_reps: Liste des répétitions réalisées par série
            target_sets: Nombre de séries cibles

        Returns:
            True si la charge doit être augmentée
        """
        if len(achieved_reps) < target_sets:
            return False

        # Si toutes les séries atteignent le target, augmenter
        successful_sets = sum(1 for reps in achieved_reps if reps >= target_reps)
        return successful_sets >= target_sets

    @staticmethod
    def calculate_next_weight(
        current_weight: float,
        progression_success: bool,
        objective: ObjectiveType,
        exercise_type: str = "strength"
    ) -> float:
        """
        Calcule le prochain poids à utiliser

        Args:
            current_weight: Poids actuel
            progression_success: Si la progression est réussie
            objective: Objectif d'entraînement
            exercise_type: Type d'exercice (strength, endurance, etc.)

        Returns:
            Nouveau poids recommandé
        """
        if not progression_success:
            return current_weight  # Maintenir le poids

        # Facteurs d'augmentation selon l'objectif
        increase_factors = {
            ObjectiveType.MUSCLE_GAIN: 0.05,    # +5%
            ObjectiveType.WEIGHT_LOSS: 0.025,   # +2.5%
            ObjectiveType.MAINTENANCE: 0.035    # +3.5%
        }

        # Ajustement selon le type d'exercice
        exercise_multipliers = {
            "strength": 1.0,
            "endurance": 0.7,
            "power": 1.2
        }

        base_increase = increase_factors.get(objective, 0.035)
        exercise_multiplier = exercise_multipliers.get(exercise_type, 1.0)

        increase = current_weight * base_increase * exercise_multiplier

        # Arrondir à 2.5kg près pour les poids libres
        if current_weight >= 20:
            increase = math.ceil(increase / 2.5) * 2.5
        else:
            increase = math.ceil(increase)

        return round(current_weight + increase, 2)

    @staticmethod
    def calculate_rest_time(
        exercise_type: str,
        objective: ObjectiveType,
        weight_percentage_1rm: float
    ) -> int:
        """
        Calcule le temps de repos recommandé entre les séries

        Args:
            exercise_type: Type d'exercice
            objective: Objectif d'entraînement
            weight_percentage_1rm: Pourcentage du 1RM utilisé

        Returns:
            Temps de repos en secondes
        """
        base_rest_times = {
            ObjectiveType.MUSCLE_GAIN: 120,     # 2 minutes
            ObjectiveType.WEIGHT_LOSS: 60,      # 1 minute
            ObjectiveType.MAINTENANCE: 90       # 1.5 minutes
        }

        base_time = base_rest_times.get(objective, 90)

        # Ajustement selon l'intensité
        if weight_percentage_1rm >= 0.85:      # 85%+ du 1RM
            return base_time + 60
        elif weight_percentage_1rm >= 0.70:    # 70-85% du 1RM
            return base_time + 30
        else:                                  # <70% du 1RM
            return base_time


class StatisticsService:
    """Service pour calculer les statistiques d'entraînement"""

    @staticmethod
    def calculate_weekly_volume(workouts_data: List[Dict]) -> Dict:
        """
        Calcule le volume d'entraînement hebdomadaire

        Args:
            workouts_data: Liste des données d'entraînements

        Returns:
            Dictionnaire avec les statistiques de volume
        """
        total_sets = 0
        total_reps = 0
        total_weight = 0
        exercises_count = 0

        for workout in workouts_data:
            for exercise in workout.get('exercises', []):
                exercises_count += 1
                for serie in exercise.get('series', []):
                    total_sets += 1
                    total_reps += serie.get('reps', 0)
                    total_weight += serie.get('weight', 0) * serie.get('reps', 0)

        return {
            'total_sets': total_sets,
            'total_reps': total_reps,
            'total_volume': round(total_weight, 2),
            'exercises_count': exercises_count,
            'average_volume_per_exercise': round(total_weight / max(exercises_count, 1), 2)
        }

    @staticmethod
    def calculate_progression_trend(
        performance_history: List[Dict],
        days_period: int = 30
    ) -> Dict:
        """
        Calcule la tendance de progression sur une période donnée

        Args:
            performance_history: Historique des performances
            days_period: Période en jours à analyser

        Returns:
            Dictionnaire avec les tendances de progression
        """
        cutoff_date = datetime.now() - timedelta(days=days_period)
        recent_data = [
            item for item in performance_history
            if datetime.fromisoformat(item['date']) >= cutoff_date
        ]

        if len(recent_data) < 2:
            return {'trend': 'insufficient_data', 'percentage_change': 0}

        # Calcul simple de progression basé sur le premier et dernier enregistrement
        first_performance = recent_data[0]
        last_performance = recent_data[-1]

        first_max = first_performance.get('max_weight', 0)
        last_max = last_performance.get('max_weight', 0)

        if first_max == 0:
            return {'trend': 'no_baseline', 'percentage_change': 0}

        percentage_change = ((last_max - first_max) / first_max) * 100

        if percentage_change > 5:
            trend = 'strong_improvement'
        elif percentage_change > 1:
            trend = 'improvement'
        elif percentage_change > -1:
            trend = 'stable'
        elif percentage_change > -5:
            trend = 'slight_decline'
        else:
            trend = 'decline'

        return {
            'trend': trend,
            'percentage_change': round(percentage_change, 2),
            'period_days': days_period,
            'data_points': len(recent_data)
        }