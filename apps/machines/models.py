from django.db import models
from django.core.validators import MinLengthValidator


class MuscleGroup(models.Model):
    """
    Modèle représentant un groupe musculaire
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom du groupe musculaire",
        help_text="Ex: Pectoraux, Biceps, Quadriceps..."
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Description détaillée du groupe musculaire"
    )
    anatomical_zone = models.CharField(
        max_length=50,
        choices=[
            ('upper_body', 'Haut du corps'),
            ('lower_body', 'Bas du corps'),
            ('core', 'Tronc/Core'),
            ('full_body', 'Corps entier'),
        ],
        default='upper_body',
        verbose_name="Zone anatomique"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Groupe musculaire"
        verbose_name_plural = "Groupes musculaires"
        ordering = ['name']

    def __str__(self):
        return self.name


class Label(models.Model):
    """
    Modèle représentant un label/tag pour catégoriser les machines
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        validators=[MinLengthValidator(2)],
        verbose_name="Nom du label",
        help_text="Ex: Cardio, Force, Isolation, Compound..."
    )
    color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name="Couleur",
        help_text="Couleur hexadécimale pour l'affichage (ex: #007bff)"
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Description",
        help_text="Description courte du label"
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name="Label principal",
        help_text="Indique si ce label est un tag principal (affiché en priorité)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Label"
        verbose_name_plural = "Labels"
        ordering = ['-is_primary', 'name']

    def __str__(self):
        return self.name


class Machine(models.Model):
    """
    Modèle représentant une machine/équipement de musculation
    """

    MACHINE_TYPES = [
        ('cardio', 'Cardio'),
        ('strength', 'Musculation'),
        ('functional', 'Fonctionnel'),
        ('free_weights', 'Poids libres'),
        ('bodyweight', 'Poids du corps'),
    ]

    DIFFICULTY_LEVELS = [
        (1, 'Débutant'),
        (2, 'Intermédiaire'),
        (3, 'Avancé'),
        (4, 'Expert'),
    ]

    # Informations de base
    name = models.CharField(
        max_length=200,
        unique=True,
        validators=[MinLengthValidator(3)],
        verbose_name="Nom de la machine",
        help_text="Nom complet et descriptif de la machine"
    )

    brand = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Marque",
        help_text="Marque/fabricant de la machine"
    )

    model = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Modèle",
        help_text="Modèle spécifique de la machine"
    )

    machine_type = models.CharField(
        max_length=20,
        choices=MACHINE_TYPES,
        default='strength',
        verbose_name="Type de machine"
    )

    # Description et utilisation
    description = models.TextField(
        verbose_name="Description",
        help_text="Description détaillée de la machine et de son utilisation"
    )

    instructions = models.TextField(
        verbose_name="Instructions d'utilisation",
        help_text="Guide détaillé pour utiliser correctement la machine"
    )

    safety_notes = models.TextField(
        blank=True,
        verbose_name="Notes de sécurité",
        help_text="Consignes de sécurité importantes"
    )

    difficulty_level = models.IntegerField(
        choices=DIFFICULTY_LEVELS,
        default=2,
        verbose_name="Niveau de difficulté"
    )

    # Relations avec groupes musculaires
    primary_muscles = models.ManyToManyField(
        MuscleGroup,
        related_name='primary_machines',
        verbose_name="Muscles principaux",
        help_text="Groupes musculaires principalement sollicités"
    )

    secondary_muscles = models.ManyToManyField(
        MuscleGroup,
        related_name='secondary_machines',
        blank=True,
        verbose_name="Muscles secondaires",
        help_text="Groupes musculaires secondairement sollicités"
    )

    # Labels et catégorisation
    labels = models.ManyToManyField(
        Label,
        blank=True,
        verbose_name="Labels",
        help_text="Labels pour catégoriser la machine"
    )

    # Caractéristiques techniques pour cardio
    supports_speed = models.BooleanField(
        default=False,
        verbose_name="Supporte la vitesse",
        help_text="Machine cardio avec réglage de vitesse"
    )

    supports_incline = models.BooleanField(
        default=False,
        verbose_name="Supporte l'inclinaison",
        help_text="Machine cardio avec réglage d'inclinaison"
    )

    supports_resistance = models.BooleanField(
        default=True,
        verbose_name="Supporte la résistance",
        help_text="Machine avec réglage de résistance/poids"
    )

    # Caractéristiques pour musculation
    min_weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Poids minimum (kg)",
        help_text="Poids minimum configurable"
    )

    max_weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Poids maximum (kg)",
        help_text="Poids maximum configurable"
    )

    weight_increment = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=2.5,
        verbose_name="Incrément de poids (kg)",
        help_text="Plus petit incrément de poids possible"
    )

    # Image et média
    image = models.ImageField(
        upload_to='machines/',
        null=True,
        blank=True,
        verbose_name="Image",
        help_text="Photo de la machine"
    )

    # Méta-données
    is_active = models.BooleanField(
        default=True,
        verbose_name="Machine active",
        help_text="Machine disponible pour utilisation"
    )

    is_maintenance = models.BooleanField(
        default=False,
        verbose_name="En maintenance",
        help_text="Machine temporairement indisponible"
    )

    gym_location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Emplacement salle",
        help_text="Zone/emplacement dans la salle de sport"
    )

    popularity_score = models.IntegerField(
        default=0,
        verbose_name="Score de popularité",
        help_text="Score basé sur l'utilisation (calculé automatiquement)"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Machine"
        verbose_name_plural = "Machines"
        ordering = ['name']
        indexes = [
            models.Index(fields=['machine_type']),
            models.Index(fields=['is_active', 'is_maintenance']),
            models.Index(fields=['popularity_score']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_machine_type_display()})"

    @property
    def is_available(self):
        """Vérifie si la machine est disponible pour utilisation"""
        return self.is_active and not self.is_maintenance

    @property
    def all_muscle_groups(self):
        """Retourne tous les groupes musculaires (primaires + secondaires)"""
        primary = list(self.primary_muscles.all())
        secondary = list(self.secondary_muscles.all())
        return primary + secondary

    @property
    def primary_labels(self):
        """Retourne les labels principaux uniquement"""
        return self.labels.filter(is_primary=True)

    def get_weight_range_display(self):
        """Retourne l'affichage de la plage de poids"""
        if self.min_weight and self.max_weight:
            return f"{self.min_weight}kg - {self.max_weight}kg"
        elif self.max_weight:
            return f"Max: {self.max_weight}kg"
        elif self.min_weight:
            return f"Min: {self.min_weight}kg"
        return "Poids libre"

    def increment_popularity(self):
        """Incrémente le score de popularité"""
        self.popularity_score += 1
        self.save(update_fields=['popularity_score'])


class MachineRating(models.Model):
    """
    Modèle pour les évaluations des machines par les utilisateurs
    """
    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name="Machine"
    )
    user = models.ForeignKey(
        'users.User',  # Forward reference
        on_delete=models.CASCADE,
        verbose_name="Utilisateur"
    )
    rating = models.IntegerField(
        choices=[(i, f"{i} étoile{'s' if i > 1 else ''}") for i in range(1, 6)],
        verbose_name="Note"
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Commentaire",
        help_text="Commentaire sur la machine"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Évaluation de machine"
        verbose_name_plural = "Évaluations de machines"
        unique_together = ['machine', 'user']  # Un utilisateur ne peut noter qu'une fois
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.machine.name} - {self.rating}/5 par {self.user.get_full_name()}"