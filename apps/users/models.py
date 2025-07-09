from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.services import ObjectiveType


class User(AbstractUser):
    """
    Modèle utilisateur étendu pour MyCoach
    """

    OBJECTIVE_CHOICES = [
        (ObjectiveType.MUSCLE_GAIN.value, 'Prise de masse'),
        (ObjectiveType.WEIGHT_LOSS.value, 'Perte de poids/Sèche'),
        (ObjectiveType.MAINTENANCE.value, 'Maintien/Forme'),
    ]

    # Remplacer username par email
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")

    # Informations personnelles étendues
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(300)],
        verbose_name="Poids (kg)",
        help_text="Poids actuel en kilogrammes"
    )

    height = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(100), MaxValueValidator(250)],
        verbose_name="Taille (cm)",
        help_text="Taille en centimètres"
    )

    age = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(13), MaxValueValidator(120)],
        verbose_name="Âge",
        help_text="Âge en années"
    )

    objective = models.CharField(
        max_length=20,
        choices=OBJECTIVE_CHOICES,
        default=ObjectiveType.MAINTENANCE.value,
        verbose_name="Objectif",
        help_text="Objectif principal d'entraînement"
    )

    # Métadonnées utilisateur
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone"
    )

    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de naissance"
    )

    profile_picture = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True,
        verbose_name="Photo de profil"
    )

    # Paramètres d'entraînement
    experience_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Débutant'),
            ('intermediate', 'Intermédiaire'),
            ('advanced', 'Avancé'),
            ('expert', 'Expert'),
        ],
        default='beginner',
        verbose_name="Niveau d'expérience"
    )

    preferred_workout_duration = models.IntegerField(
        default=60,
        validators=[MinValueValidator(15), MaxValueValidator(180)],
        verbose_name="Durée d'entraînement préférée (min)",
        help_text="Durée souhaitée pour une séance en minutes"
    )

    weekly_workout_frequency = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name="Fréquence hebdomadaire",
        help_text="Nombre de séances par semaine"
    )

    # Préférences et restrictions
    has_injuries = models.BooleanField(
        default=False,
        verbose_name="Blessures/Limitations",
        help_text="Cochez si vous avez des blessures ou limitations"
    )

    injury_notes = models.TextField(
        blank=True,
        verbose_name="Notes sur les blessures",
        help_text="Décrivez vos blessures ou limitations"
    )

    # Paramètres de notification
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="Notifications email"
    )

    workout_reminders = models.BooleanField(
        default=True,
        verbose_name="Rappels d'entraînement"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_workout = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernier entraînement"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    @property
    def imc(self):
        """Calcule l'IMC de l'utilisateur"""
        if self.weight and self.height:
            from apps.core.services import IMCService
            return IMCService.calculate_imc(float(self.weight), self.height)
        return None

    @property
    def imc_interpretation(self):
        """Retourne l'interprétation de l'IMC"""
        imc = self.imc
        if imc:
            from apps.core.services import IMCService
            return IMCService.interpret_imc(imc)
        return None

    @property
    def objective_enum(self):
        """Retourne l'objectif sous forme d'enum"""
        return ObjectiveType(self.objective)

    def update_last_workout(self):
        """Met à jour la date du dernier entraînement"""
        from django.utils import timezone
        self.last_workout = timezone.now()
        self.save(update_fields=['last_workout'])

    def get_workout_stats(self, days=30):
        """Retourne les statistiques d'entraînement"""
        from datetime import timedelta
        from django.utils import timezone
        from apps.workouts.models import Workout

        cutoff_date = timezone.now() - timedelta(days=days)
        workouts = Workout.objects.filter(
            user=self,
            date__gte=cutoff_date
        )

        return {
            'total_workouts': workouts.count(),
            'days_period': days,
            'average_per_week': round(workouts.count() / (days / 7), 1),
            'last_workout': self.last_workout
        }