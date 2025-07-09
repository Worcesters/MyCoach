from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Interface d'administration pour le modèle User personnalisé"""

    # Champs affichés dans la liste des utilisateurs
    list_display = (
        'email', 'first_name', 'last_name', 'is_active',
        'is_staff', 'date_joined', 'last_workout'
    )

    # Champs pour filtrer
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'date_joined',
        'objective', 'experience_level'
    )

    # Champs de recherche
    search_fields = ('email', 'first_name', 'last_name')

    # Ordre par défaut
    ordering = ('-date_joined',)

    # Configuration des fieldsets pour l'édition
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Informations personnelles'), {
            'fields': (
                'first_name', 'last_name', 'phone', 'birth_date',
                'profile_picture'
            )
        }),
        (_('Données physiques'), {
            'fields': ('weight', 'height', 'age')
        }),
        (_('Objectifs et préférences'), {
            'fields': (
                'objective', 'experience_level',
                'preferred_workout_duration', 'weekly_workout_frequency'
            )
        }),
        (_('Limitations et blessures'), {
            'fields': ('has_injuries', 'injury_notes')
        }),
        (_('Notifications'), {
            'fields': ('email_notifications', 'workout_reminders')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
        }),
        (_('Dates importantes'), {
            'fields': ('last_login', 'date_joined', 'last_workout')
        }),
    )

    # Configuration pour l'ajout d'un nouvel utilisateur
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name',
                'password1', 'password2'
            ),
        }),
    )

    # Champs en lecture seule
    readonly_fields = ('date_joined', 'last_login')

    # Méthodes personnalisées pour l'affichage
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Nom complet'

    def imc_display(self, obj):
        imc = obj.imc
        if imc:
            interp = obj.imc_interpretation
            return f"{imc:.1f} ({interp})"
        return "Non calculé"
    imc_display.short_description = 'IMC'