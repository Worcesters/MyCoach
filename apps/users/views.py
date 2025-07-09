from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db import transaction

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=password
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'email', 'date_joined')

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Vue d'inscription pour créer un nouveau compte utilisateur.
    """
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        try:
            with transaction.atomic():
                user = serializer.save()
                return Response({
                    'message': 'Compte créé avec succès',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': 'Erreur lors de la création du compte',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({
        'error': 'Données invalides',
        'details': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Vue pour récupérer et mettre à jour le profil utilisateur.
    """
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profil mis à jour avec succès',
                'user': serializer.data
            })
        return Response({
            'error': 'Données invalides',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)