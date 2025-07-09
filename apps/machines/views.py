from django.db.models import Q, Avg
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .models import Machine, MuscleGroup, Label, MachineRating
from .serializers import (
    MachineListSerializer, MachineDetailSerializer, MachineCreateUpdateSerializer,
    MuscleGroupSerializer, LabelSerializer, MachineRatingSerializer,
    MachineRatingCreateSerializer, MachineSearchSerializer
)


class MuscleGroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les groupes musculaires (lecture seule)
    """
    queryset = MuscleGroup.objects.all()
    serializer_class = MuscleGroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'anatomical_zone']
    ordering = ['name']


class LabelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les labels (lecture seule)
    """
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_primary']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'is_primary']
    ordering = ['-is_primary', 'name']


class MachineViewSet(viewsets.ModelViewSet):
    """
    ViewSet complet pour les machines
    """
    queryset = Machine.objects.select_related().prefetch_related(
        'primary_muscles', 'secondary_muscles', 'labels', 'ratings'
    )
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'brand', 'model', 'description']
    ordering_fields = ['name', 'popularity_score', 'created_at', 'difficulty_level']
    ordering = ['name']

    filterset_fields = {
        'machine_type': ['exact', 'in'],
        'difficulty_level': ['exact', 'in', 'gte', 'lte'],
        'is_active': ['exact'],
        'is_maintenance': ['exact'],
        'supports_speed': ['exact'],
        'supports_incline': ['exact'],
        'supports_resistance': ['exact'],
        'primary_muscles': ['exact', 'in'],
        'labels': ['exact', 'in'],
    }

    def get_serializer_class(self):
        """Choix du serializer selon l'action"""
        if self.action == 'list':
            return MachineListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return MachineCreateUpdateSerializer
        else:
            return MachineDetailSerializer

    def get_queryset(self):
        """Filtrage personnalisé du queryset"""
        queryset = super().get_queryset()

        # Filtrer par disponibilité si demandé
        is_available = self.request.query_params.get('is_available')
        if is_available is not None:
            if is_available.lower() == 'true':
                queryset = queryset.filter(is_active=True, is_maintenance=False)
            elif is_available.lower() == 'false':
                queryset = queryset.filter(Q(is_active=False) | Q(is_maintenance=True))

        # Filtrer les machines cardio
        supports_cardio = self.request.query_params.get('supports_cardio')
        if supports_cardio is not None and supports_cardio.lower() == 'true':
            queryset = queryset.filter(
                Q(supports_speed=True) | Q(supports_incline=True)
            )

        return queryset

    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """
        Marquer une machine comme utilisée (incrémente la popularité)
        """
        machine = self.get_object()
        machine.increment_popularity()
        return Response({
            'message': 'Utilisation enregistrée',
            'popularity_score': machine.popularity_score
        })

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Retourne les machines les plus populaires
        """
        popular_machines = self.get_queryset().filter(
            is_active=True, is_maintenance=False
        ).order_by('-popularity_score')[:10]

        serializer = MachineListSerializer(popular_machines, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_muscle_group(self, request):
        """
        Retourne les machines groupées par groupe musculaire
        """
        muscle_group_id = request.query_params.get('muscle_group_id')
        if not muscle_group_id:
            return Response(
                {'error': 'muscle_group_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        machines = self.get_queryset().filter(
            Q(primary_muscles__id=muscle_group_id) |
            Q(secondary_muscles__id=muscle_group_id),
            is_active=True,
            is_maintenance=False
        ).distinct()

        serializer = MachineListSerializer(machines, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def search(self, request):
        """
        Recherche avancée de machines
        """
        search_serializer = MachineSearchSerializer(data=request.data)
        if not search_serializer.is_valid():
            return Response(
                search_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        data = search_serializer.validated_data
        queryset = self.get_queryset()

        # Recherche textuelle
        if 'q' in data:
            queryset = queryset.filter(
                Q(name__icontains=data['q']) |
                Q(brand__icontains=data['q']) |
                Q(description__icontains=data['q'])
            )

        # Filtres spécifiques
        if 'machine_type' in data:
            queryset = queryset.filter(machine_type=data['machine_type'])

        if 'difficulty_level' in data:
            queryset = queryset.filter(difficulty_level=data['difficulty_level'])

        if 'muscle_groups' in data:
            queryset = queryset.filter(
                Q(primary_muscles__id__in=data['muscle_groups']) |
                Q(secondary_muscles__id__in=data['muscle_groups'])
            ).distinct()

        if 'labels' in data:
            queryset = queryset.filter(labels__id__in=data['labels']).distinct()

        if 'is_available' in data and data['is_available']:
            queryset = queryset.filter(is_active=True, is_maintenance=False)

        if 'supports_cardio' in data and data['supports_cardio']:
            queryset = queryset.filter(
                Q(supports_speed=True) | Q(supports_incline=True)
            )

        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MachineListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MachineListSerializer(queryset, many=True)
        return Response(serializer.data)


class MachineRatingViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les évaluations de machines
    """
    queryset = MachineRating.objects.select_related('machine', 'user')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['machine', 'rating']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Choix du serializer selon l'action"""
        if self.action in ['create']:
            return MachineRatingCreateSerializer
        return MachineRatingSerializer

    def get_queryset(self):
        """Filtrer les évaluations selon l'utilisateur"""
        queryset = super().get_queryset()

        # Si paramètre my_ratings, ne retourner que les évaluations de l'utilisateur
        if self.request.query_params.get('my_ratings') == 'true':
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def perform_create(self, serializer):
        """Assigner l'utilisateur lors de la création"""
        # Vérifier si l'utilisateur a déjà évalué cette machine
        machine = serializer.validated_data['machine']
        if MachineRating.objects.filter(
            user=self.request.user,
            machine=machine
        ).exists():
            raise serializers.ValidationError(
                "Vous avez déjà évalué cette machine. Utilisez PUT pour la modifier."
            )

        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def machine_stats(self, request):
        """
        Statistiques d'évaluations pour une machine
        """
        machine_id = request.query_params.get('machine_id')
        if not machine_id:
            return Response(
                {'error': 'machine_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ratings = self.queryset.filter(machine_id=machine_id)

        if not ratings.exists():
            return Response({
                'machine_id': machine_id,
                'total_ratings': 0,
                'average_rating': None,
                'rating_distribution': {}
            })

        # Calculer les statistiques
        avg_rating = ratings.aggregate(avg=Avg('rating'))['avg']
        total_ratings = ratings.count()

        # Distribution des notes
        distribution = {}
        for i in range(1, 6):
            distribution[str(i)] = ratings.filter(rating=i).count()

        return Response({
            'machine_id': machine_id,
            'total_ratings': total_ratings,
            'average_rating': round(avg_rating, 1) if avg_rating else None,
            'rating_distribution': distribution
        })