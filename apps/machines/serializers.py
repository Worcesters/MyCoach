from rest_framework import serializers
from .models import Machine, MuscleGroup, Label, MachineRating


class MuscleGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MuscleGroup
        fields = ['id', 'name', 'description', 'anatomical_zone']


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['id', 'name', 'color', 'description', 'is_primary']


class MachineRatingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = MachineRating
        fields = ['id', 'rating', 'comment', 'user_name', 'created_at']
        read_only_fields = ['created_at']


class MachineListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des machines"""
    primary_muscles = MuscleGroupSerializer(many=True, read_only=True)
    primary_labels = LabelSerializer(many=True, read_only=True)
    machine_type_display = serializers.CharField(source='get_machine_type_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_level_display', read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    weight_range = serializers.CharField(source='get_weight_range_display', read_only=True)

    class Meta:
        model = Machine
        fields = [
            'id', 'name', 'brand', 'machine_type', 'machine_type_display',
            'difficulty_level', 'difficulty_display', 'primary_muscles',
            'primary_labels', 'image', 'is_available', 'weight_range',
            'popularity_score'
        ]


class MachineDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour les détails d'une machine"""
    primary_muscles = MuscleGroupSerializer(many=True, read_only=True)
    secondary_muscles = MuscleGroupSerializer(many=True, read_only=True)
    labels = LabelSerializer(many=True, read_only=True)
    ratings = MachineRatingSerializer(many=True, read_only=True)

    machine_type_display = serializers.CharField(source='get_machine_type_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_level_display', read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    weight_range = serializers.CharField(source='get_weight_range_display', read_only=True)
    all_muscle_groups = MuscleGroupSerializer(many=True, read_only=True)

    # Statistiques calculées
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()

    class Meta:
        model = Machine
        fields = [
            'id', 'name', 'brand', 'model', 'machine_type', 'machine_type_display',
            'description', 'instructions', 'safety_notes', 'difficulty_level',
            'difficulty_display', 'primary_muscles', 'secondary_muscles',
            'all_muscle_groups', 'labels', 'supports_speed', 'supports_incline',
            'supports_resistance', 'min_weight', 'max_weight', 'weight_increment',
            'image', 'is_available', 'gym_location', 'popularity_score',
            'weight_range', 'ratings', 'average_rating', 'total_ratings',
            'created_at', 'updated_at'
        ]

    def get_average_rating(self, obj):
        """Calcule la note moyenne de la machine"""
        ratings = obj.ratings.all()
        if ratings:
            return round(sum(r.rating for r in ratings) / len(ratings), 1)
        return None

    def get_total_ratings(self, obj):
        """Retourne le nombre total d'évaluations"""
        return obj.ratings.count()


class MachineCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la création et modification des machines"""

    class Meta:
        model = Machine
        fields = [
            'name', 'brand', 'model', 'machine_type', 'description',
            'instructions', 'safety_notes', 'difficulty_level',
            'primary_muscles', 'secondary_muscles', 'labels',
            'supports_speed', 'supports_incline', 'supports_resistance',
            'min_weight', 'max_weight', 'weight_increment', 'image',
            'gym_location', 'is_active', 'is_maintenance'
        ]

    def validate(self, data):
        """Validation personnalisée"""
        # Vérifier que min_weight <= max_weight
        min_weight = data.get('min_weight')
        max_weight = data.get('max_weight')

        if min_weight and max_weight and min_weight > max_weight:
            raise serializers.ValidationError(
                "Le poids minimum ne peut pas être supérieur au poids maximum."
            )

        # Vérifier que weight_increment est cohérent
        weight_increment = data.get('weight_increment', 0)
        if weight_increment <= 0:
            raise serializers.ValidationError(
                "L'incrément de poids doit être positif."
            )

        return data


class MachineRatingCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer une évaluation de machine"""

    class Meta:
        model = MachineRating
        fields = ['machine', 'rating', 'comment']

    def validate_rating(self, value):
        """Validation de la note"""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("La note doit être entre 1 et 5.")
        return value

    def create(self, validated_data):
        """Création avec utilisateur automatique"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MachineSearchSerializer(serializers.Serializer):
    """Serializer pour les paramètres de recherche de machines"""
    q = serializers.CharField(required=False, help_text="Recherche textuelle")
    machine_type = serializers.ChoiceField(
        choices=Machine.MACHINE_TYPES,
        required=False,
        help_text="Type de machine"
    )
    difficulty_level = serializers.ChoiceField(
        choices=Machine.DIFFICULTY_LEVELS,
        required=False,
        help_text="Niveau de difficulté"
    )
    muscle_groups = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="IDs des groupes musculaires"
    )
    labels = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="IDs des labels"
    )
    is_available = serializers.BooleanField(
        required=False,
        help_text="Machines disponibles uniquement"
    )
    supports_cardio = serializers.BooleanField(
        required=False,
        help_text="Machines cardio (vitesse ou inclinaison)"
    )