from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import json


class WorkoutPlan(models.Model):
    """
    Modèle pour la planification des séances d'entraînement
    """

    REPEAT_TYPES = [
        ('none', 'Aucune répétition'),
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='workout_plans',
        verbose_name="Utilisateur"
    )

    template = models.ForeignKey(
        'workouts.WorkoutTemplate',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Template de séance"
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Titre de la séance planifiée"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )

    # Planification temporelle
    scheduled_date = models.DateTimeField(
        verbose_name="Date et heure programmées"
    )

    duration_minutes = models.IntegerField(
        default=60,
        validators=[MinValueValidator(15), MaxValueValidator(300)],
        verbose_name="Durée prévue (minutes)"
    )

    # Répétition
    repeat_type = models.CharField(
        max_length=20,
        choices=REPEAT_TYPES,
        default='none',
        verbose_name="Type de répétition"
    )

    repeat_interval = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(30)],
        verbose_name="Intervalle de répétition",
        help_text="Par ex: tous les 2 jours, toutes les 3 semaines"
    )

    repeat_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="Répéter jusqu'au",
        help_text="Date de fin de la répétition"
    )

    # Statut et priorité
    is_active = models.BooleanField(
        default=True,
        verbose_name="Plan actif"
    )

    priority = models.IntegerField(
        choices=[(i, f"Priorité {i}") for i in range(1, 6)],
        default=3,
        verbose_name="Priorité",
        help_text="1 = Très faible, 5 = Très élevée"
    )

    # Notifications
    reminder_enabled = models.BooleanField(
        default=True,
        verbose_name="Rappel activé"
    )

    reminder_minutes_before = models.IntegerField(
        default=30,
        validators=[MinValueValidator(5), MaxValueValidator(1440)],
        verbose_name="Rappel X minutes avant",
        help_text="Nombre de minutes avant la séance pour le rappel"
    )

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Relation avec la séance créée
    workout_created = models.ForeignKey(
        'workouts.Workout',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Séance créée"
    )

    class Meta:
        verbose_name = "Plan d'entraînement"
        verbose_name_plural = "Plans d'entraînement"
        ordering = ['scheduled_date']
        indexes = [
            models.Index(fields=['user', 'scheduled_date']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.title} - {self.scheduled_date.strftime('%d/%m/%Y %H:%M')}"

    @property
    def is_past_due(self):
        """Vérifie si la séance est en retard"""
        return self.scheduled_date < timezone.now() and not self.workout_created

    @property
    def is_today(self):
        """Vérifie si la séance est prévue aujourd'hui"""
        today = timezone.now().date()
        return self.scheduled_date.date() == today

    def create_workout(self):
        """Crée une séance d'entraînement basée sur ce plan"""
        if self.workout_created:
            return self.workout_created

        from apps.workouts.models import Workout

        workout = Workout.objects.create(
            user=self.user,
            template=self.template,
            name=self.title,
            description=self.description,
            date=self.scheduled_date,
            planned_duration_minutes=self.duration_minutes,
            status='planned'
        )

        self.workout_created = workout
        self.save(update_fields=['workout_created'])

        return workout


class CSVImport(models.Model):
    """
    Modèle pour l'import de données CSV
    """

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours de traitement'),
        ('completed', 'Terminé'),
        ('failed', 'Échec'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='csv_imports',
        verbose_name="Utilisateur"
    )

    file = models.FileField(
        upload_to='csv_imports/',
        verbose_name="Fichier CSV"
    )

    filename = models.CharField(
        max_length=255,
        verbose_name="Nom du fichier"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut"
    )

    # Résultats de l'import
    total_rows = models.IntegerField(
        default=0,
        verbose_name="Nombre total de lignes"
    )

    successful_imports = models.IntegerField(
        default=0,
        verbose_name="Imports réussis"
    )

    failed_imports = models.IntegerField(
        default=0,
        verbose_name="Imports échoués"
    )

    # Logs et erreurs
    import_log = models.TextField(
        blank=True,
        verbose_name="Log d'import",
        help_text="Détails du processus d'import"
    )

    error_details = models.TextField(
        blank=True,
        verbose_name="Détails des erreurs"
    )

    # Options d'import
    import_options = models.JSONField(
        default=dict,
        verbose_name="Options d'import",
        help_text="Configuration de l'import (format, mapping, etc.)"
    )

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Traité le"
    )

    class Meta:
        verbose_name = "Import CSV"
        verbose_name_plural = "Imports CSV"
        ordering = ['-created_at']

    def __str__(self):
        return f"Import {self.filename} - {self.user.get_full_name()}"

    @property
    def success_rate(self):
        """Calcule le taux de réussite de l'import"""
        if self.total_rows == 0:
            return 0
        return round((self.successful_imports / self.total_rows) * 100, 1)

    def start_processing(self):
        """Démarre le traitement de l'import"""
        self.status = 'processing'
        self.save(update_fields=['status'])

    def complete_processing(self, success_count, failed_count, log_message=""):
        """Termine le traitement de l'import"""
        self.status = 'completed'
        self.successful_imports = success_count
        self.failed_imports = failed_count
        self.total_rows = success_count + failed_count
        self.processed_at = timezone.now()
        self.import_log = log_message
        self.save()

    def fail_processing(self, error_message):
        """Marque l'import comme échoué"""
        self.status = 'failed'
        self.error_details = error_message
        self.processed_at = timezone.now()
        self.save()


class CalendarEvent(models.Model):
    """
    Modèle pour les événements du calendrier (séances, notes, etc.)
    """

    EVENT_TYPES = [
        ('workout', 'Séance d\'entraînement'),
        ('rest', 'Jour de repos'),
        ('note', 'Note personnelle'),
        ('goal', 'Objectif'),
        ('reminder', 'Rappel'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='calendar_events',
        verbose_name="Utilisateur"
    )

    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPES,
        verbose_name="Type d'événement"
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Titre"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )

    # Temporalité
    start_date = models.DateTimeField(
        verbose_name="Date de début"
    )

    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de fin"
    )

    all_day = models.BooleanField(
        default=False,
        verbose_name="Toute la journée"
    )

    # Relations
    workout = models.ForeignKey(
        'workouts.Workout',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Séance associée"
    )

    workout_plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Plan associé"
    )

    # Apparence
    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name="Couleur",
        help_text="Couleur hexadécimale (ex: #007bff)"
    )

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Événement du calendrier"
        verbose_name_plural = "Événements du calendrier"
        ordering = ['start_date']
        indexes = [
            models.Index(fields=['user', 'start_date']),
            models.Index(fields=['event_type']),
        ]

    def __str__(self):
        return f"{self.title} ({self.start_date.strftime('%d/%m/%Y')})"

    @property
    def duration(self):
        """Calcule la durée de l'événement"""
        if self.end_date:
            return self.end_date - self.start_date
        return None


class WeeklyTemplate(models.Model):
    """
    Modèle pour les templates de semaine d'entraînement
    """

    DAYS_OF_WEEK = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='weekly_templates',
        verbose_name="Utilisateur"
    )

    name = models.CharField(
        max_length=200,
        verbose_name="Nom du template"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )

    is_active = models.BooleanField(
        default=False,
        verbose_name="Template actif",
        help_text="Un seul template peut être actif à la fois"
    )

    # Configuration par jour
    monday_template = models.ForeignKey(
        'workouts.WorkoutTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='weekly_mondays',
        verbose_name="Template du lundi"
    )

    tuesday_template = models.ForeignKey(
        'workouts.WorkoutTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='weekly_tuesdays',
        verbose_name="Template du mardi"
    )

    wednesday_template = models.ForeignKey(
        'workouts.WorkoutTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='weekly_wednesdays',
        verbose_name="Template du mercredi"
    )

    thursday_template = models.ForeignKey(
        'workouts.WorkoutTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='weekly_thursdays',
        verbose_name="Template du jeudi"
    )

    friday_template = models.ForeignKey(
        'workouts.WorkoutTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='weekly_fridays',
        verbose_name="Template du vendredi"
    )

    saturday_template = models.ForeignKey(
        'workouts.WorkoutTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='weekly_saturdays',
        verbose_name="Template du samedi"
    )

    sunday_template = models.ForeignKey(
        'workouts.WorkoutTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='weekly_sundays',
        verbose_name="Template du dimanche"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Template hebdomadaire"
        verbose_name_plural = "Templates hebdomadaires"
        ordering = ['-is_active', '-created_at']

    def __str__(self):
        status = " (Actif)" if self.is_active else ""
        return f"{self.name}{status}"

    def get_template_for_day(self, day_of_week):
        """Retourne le template pour un jour donné (0=lundi, 6=dimanche)"""
        day_templates = {
            0: self.monday_template,
            1: self.tuesday_template,
            2: self.wednesday_template,
            3: self.thursday_template,
            4: self.friday_template,
            5: self.saturday_template,
            6: self.sunday_template,
        }
        return day_templates.get(day_of_week)

    def set_template_for_day(self, day_of_week, template):
        """Définit le template pour un jour donné"""
        day_fields = {
            0: 'monday_template',
            1: 'tuesday_template',
            2: 'wednesday_template',
            3: 'thursday_template',
            4: 'friday_template',
            5: 'saturday_template',
            6: 'sunday_template',
        }

        field_name = day_fields.get(day_of_week)
        if field_name:
            setattr(self, field_name, template)
            self.save(update_fields=[field_name])

    def activate(self):
        """Active ce template (désactive les autres)"""
        # Désactiver tous les autres templates de l'utilisateur
        WeeklyTemplate.objects.filter(
            user=self.user,
            is_active=True
        ).exclude(id=self.id).update(is_active=False)

        # Activer celui-ci
        self.is_active = True
        self.save(update_fields=['is_active'])

    def generate_week_plan(self, start_date):
        """Génère un plan de la semaine à partir de ce template"""
        from datetime import timedelta

        plans_created = []

        for day_offset in range(7):
            day_date = start_date + timedelta(days=day_offset)
            day_of_week = day_date.weekday()  # 0=lundi, 6=dimanche

            template = self.get_template_for_day(day_of_week)
            if template:
                # Créer un plan pour ce jour
                plan = WorkoutPlan.objects.create(
                    user=self.user,
                    template=template,
                    title=template.name,
                    description=f"Généré à partir du template '{self.name}'",
                    scheduled_date=day_date.replace(hour=8, minute=0),  # 8h par défaut
                    duration_minutes=template.target_duration_minutes,
                )
                plans_created.append(plan)

        return plans_created