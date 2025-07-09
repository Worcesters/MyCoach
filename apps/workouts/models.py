from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class WorkoutTemplate(models.Model):
    """
    Modèle pour les templates de séances d'entraînement
    """
    name = models.CharField(
        max_length=200,
        verbose_name="Nom du template"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name="Créé par"
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Template public",
        help_text="Visible par tous les utilisateurs"
    )
    target_duration_minutes = models.IntegerField(
        default=60,
        validators=[MinValueValidator(15), MaxValueValidator(180)],
        verbose_name="Durée cible (minutes)"
    )
    difficulty_level = models.IntegerField(
        choices=[(i, f"Niveau {i}") for i in range(1, 6)],
        default=2,
        verbose_name="Niveau de difficulté"
    )
    tags = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Tags",
        help_text="Tags séparés par des virgules"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Template d'entraînement"
        verbose_name_plural = "Templates d'entraînements"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Workout(models.Model):
    """
    Modèle représentant une séance d'entraînement
    """

    STATUS_CHOICES = [
        ('planned', 'Planifiée'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='workouts',
        verbose_name="Utilisateur"
    )

    template = models.ForeignKey(
        WorkoutTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Template utilisé"
    )

    name = models.CharField(
        max_length=200,
        verbose_name="Nom de la séance"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )

    date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date de la séance"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planned',
        verbose_name="Statut"
    )

    # Durées et statistiques
    planned_duration_minutes = models.IntegerField(
        default=60,
        validators=[MinValueValidator(15), MaxValueValidator(300)],
        verbose_name="Durée planifiée (minutes)"
    )

    actual_duration_minutes = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(300)],
        verbose_name="Durée réelle (minutes)"
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Heure de début"
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Heure de fin"
    )

    # Évaluation de la séance
    difficulty_felt = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, f"{i}/5") for i in range(1, 6)],
        verbose_name="Difficulté ressentie"
    )

    satisfaction = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, f"{i}/5") for i in range(1, 6)],
        verbose_name="Satisfaction"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Notes personnelles"
    )

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Séance d'entraînement"
        verbose_name_plural = "Séances d'entraînement"
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} - {self.user.get_full_name()} ({self.date.strftime('%d/%m/%Y')})"

    @property
    def total_exercises(self):
        """Retourne le nombre total d'exercices"""
        return self.exercises.count()

    @property
    def total_sets(self):
        """Retourne le nombre total de séries"""
        return sum(exercise.series.count() for exercise in self.exercises.all())

    @property
    def total_volume(self):
        """Calcule le volume total de la séance (poids × répétitions)"""
        total = 0
        for exercise in self.exercises.all():
            for serie in exercise.series.all():
                if serie.weight and serie.reps:
                    total += float(serie.weight) * serie.reps
        return round(total, 2)

    def start_workout(self):
        """Démarre la séance"""
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def complete_workout(self):
        """Termine la séance"""
        self.status = 'completed'
        self.completed_at = timezone.now()

        if self.started_at:
            duration = self.completed_at - self.started_at
            self.actual_duration_minutes = int(duration.total_seconds() / 60)

        # Mettre à jour la date du dernier entraînement de l'utilisateur
        self.user.update_last_workout()

        self.save(update_fields=['status', 'completed_at', 'actual_duration_minutes'])


class Exercise(models.Model):
    """
    Modèle représentant un exercice dans une séance
    """
    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name='exercises',
        verbose_name="Séance"
    )

    machine = models.ForeignKey(
        'machines.Machine',
        on_delete=models.CASCADE,
        verbose_name="Machine/Équipement"
    )

    order = models.PositiveIntegerField(
        default=1,
        verbose_name="Ordre dans la séance"
    )

    # Configuration de l'exercice
    target_sets = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Séries cibles"
    )

    target_reps = models.IntegerField(
        default=12,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Répétitions cibles"
    )

    target_weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Poids cible (kg)"
    )

    # Pour exercices cardio
    target_duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(7200)],
        verbose_name="Durée cible (secondes)"
    )

    target_distance_meters = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(100), MaxValueValidator(50000)],
        verbose_name="Distance cible (mètres)"
    )

    # Temps de repos
    rest_seconds = models.IntegerField(
        default=90,
        validators=[MinValueValidator(30), MaxValueValidator(600)],
        verbose_name="Temps de repos (secondes)"
    )

    # Progression intelligente
    auto_progression = models.BooleanField(
        default=True,
        verbose_name="Progression automatique",
        help_text="Ajuster automatiquement le poids selon les performances"
    )

    # Notes spécifiques à l'exercice
    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )

    # Statut
    completed = models.BooleanField(
        default=False,
        verbose_name="Exercice terminé"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Exercice"
        verbose_name_plural = "Exercices"
        ordering = ['workout', 'order']
        unique_together = ['workout', 'order']

    def __str__(self):
        return f"{self.machine.name} - {self.workout.name}"

    @property
    def completed_sets(self):
        """Retourne le nombre de séries effectuées"""
        return self.series.filter(completed=True).count()

    @property
    def progress_percentage(self):
        """Calcule le pourcentage de progression de l'exercice"""
        if self.target_sets == 0:
            return 0
        return min(100, (self.completed_sets / self.target_sets) * 100)

    def calculate_suggested_weight(self):
        """Calcule le poids suggéré pour la prochaine séance"""
        if not self.auto_progression:
            return self.target_weight

        from apps.core.services import ProgressionService

        # Récupérer les répétitions effectuées
        achieved_reps = [s.reps for s in self.series.filter(completed=True) if s.reps]

        if not achieved_reps:
            return self.target_weight

        progression_success = ProgressionService.should_increase_weight(
            self.target_reps, achieved_reps, self.target_sets
        )

        return ProgressionService.calculate_next_weight(
            float(self.target_weight) if self.target_weight else 0,
            progression_success,
            self.workout.user.objective_enum,
            'cardio' if self.machine.machine_type == 'cardio' else 'strength'
        )


class Serie(models.Model):
    """
    Modèle représentant une série d'un exercice
    """
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='series',
        verbose_name="Exercice"
    )

    set_number = models.PositiveIntegerField(
        verbose_name="Numéro de série"
    )

    # Résultats de la série
    reps = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(200)],
        verbose_name="Répétitions effectuées"
    )

    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Poids utilisé (kg)"
    )

    # Pour exercices cardio
    duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(7200)],
        verbose_name="Durée (secondes)"
    )

    distance_meters = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(50000)],
        verbose_name="Distance (mètres)"
    )

    speed_kmh = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.1), MaxValueValidator(50)],
        verbose_name="Vitesse (km/h)"
    )

    incline_percentage = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(30)],
        verbose_name="Inclinaison (%)"
    )

    # Métadonnées
    completed = models.BooleanField(
        default=False,
        verbose_name="Série terminée"
    )

    rpe = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, f"RPE {i}") for i in range(1, 11)],
        verbose_name="RPE (Rate of Perceived Exertion)",
        help_text="Échelle de 1 à 10 de l'effort perçu"
    )

    rest_seconds_actual = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1800)],
        verbose_name="Temps de repos réel (secondes)"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Heure de fin"
    )

    class Meta:
        verbose_name = "Série"
        verbose_name_plural = "Séries"
        ordering = ['exercise', 'set_number']
        unique_together = ['exercise', 'set_number']

    def __str__(self):
        return f"Série {self.set_number} - {self.exercise}"

    @property
    def volume(self):
        """Calcule le volume de la série (poids × répétitions)"""
        if self.weight and self.reps:
            return float(self.weight) * self.reps
        return 0

    @property
    def estimated_1rm(self):
        """Estime le 1RM pour cette série"""
        if self.weight and self.reps and self.reps > 0:
            from apps.core.services import OneRMService
            return OneRMService.calculate_brzycki(float(self.weight), self.reps)
        return None

    def complete_set(self):
        """Marque la série comme terminée"""
        self.completed = True
        self.completed_at = timezone.now()
        self.save(update_fields=['completed', 'completed_at'])


class PerformanceRecord(models.Model):
    """
    Modèle pour enregistrer les records de performance
    """

    RECORD_TYPES = [
        ('1rm', '1RM (Une répétition maximum)'),
        ('volume', 'Volume maximum'),
        ('endurance', 'Endurance maximum'),
        ('personal', 'Record personnel'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='performance_records',
        verbose_name="Utilisateur"
    )

    machine = models.ForeignKey(
        'machines.Machine',
        on_delete=models.CASCADE,
        verbose_name="Machine"
    )

    record_type = models.CharField(
        max_length=20,
        choices=RECORD_TYPES,
        verbose_name="Type de record"
    )

    # Valeurs du record
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Poids (kg)"
    )

    reps = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        verbose_name="Répétitions"
    )

    duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(86400)],
        verbose_name="Durée (secondes)"
    )

    distance_meters = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100000)],
        verbose_name="Distance (mètres)"
    )

    # Métadonnées
    achieved_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date du record"
    )

    workout = models.ForeignKey(
        Workout,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Séance associée"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )

    is_verified = models.BooleanField(
        default=True,
        verbose_name="Record vérifié",
        help_text="Record confirmé et validé"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Record de performance"
        verbose_name_plural = "Records de performance"
        ordering = ['-achieved_at']
        indexes = [
            models.Index(fields=['user', 'machine', 'record_type']),
        ]

    def __str__(self):
        if self.weight and self.reps:
            return f"{self.user.get_full_name()} - {self.machine.name}: {self.weight}kg × {self.reps}"
        elif self.duration_seconds:
            minutes = self.duration_seconds // 60
            seconds = self.duration_seconds % 60
            return f"{self.user.get_full_name()} - {self.machine.name}: {minutes}:{seconds:02d}"
        return f"{self.user.get_full_name()} - {self.machine.name}: {self.get_record_type_display()}"


class WorkoutProgram(models.Model):
    """
    Modèle pour les programmes d'entraînement
    """
    name = models.CharField(
        max_length=200,
        verbose_name="Nom du programme"
    )

    description = models.TextField(
        verbose_name="Description du programme"
    )

    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name="Créé par"
    )

    is_public = models.BooleanField(
        default=False,
        verbose_name="Programme public"
    )

    duration_weeks = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(52)],
        verbose_name="Durée en semaines"
    )

    workouts_per_week = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name="Séances par semaine"
    )

    difficulty_level = models.IntegerField(
        choices=[(i, f"Niveau {i}") for i in range(1, 6)],
        default=2,
        verbose_name="Niveau de difficulté"
    )

    templates = models.ManyToManyField(
        WorkoutTemplate,
        blank=True,
        verbose_name="Templates inclus"
    )

    tags = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Tags"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Programme d'entraînement"
        verbose_name_plural = "Programmes d'entraînement"
        ordering = ['-created_at']

    def __str__(self):
        return self.name