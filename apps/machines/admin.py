from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.forms import CheckboxSelectMultiple

from .models import Machine, MuscleGroup, Label, MachineRating


@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'anatomical_zone', 'created_at']
    list_filter = ['anatomical_zone', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'description', 'anatomical_zone')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    list_editable = ['is_primary']

    def color_display(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            obj.color,
            obj.color
        )
    color_display.short_description = 'Couleur'

    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'description', 'color', 'is_primary')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


class MachineRatingInline(admin.TabularInline):
    model = MachineRating
    extra = 0
    readonly_fields = ['created_at']
    can_delete = True


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'machine_type', 'difficulty_level', 'is_available_display',
        'is_active', 'is_maintenance', 'popularity_score', 'get_weight_range_display'
    ]
    list_filter = [
        'machine_type', 'difficulty_level', 'is_active', 'is_maintenance',
        'supports_speed', 'supports_incline', 'supports_resistance',
        'primary_muscles', 'labels'
    ]
    search_fields = ['name', 'brand', 'model', 'description']
    readonly_fields = ['created_at', 'updated_at', 'popularity_score']
    list_editable = ['is_active', 'is_maintenance']
    filter_horizontal = ['primary_muscles', 'secondary_muscles', 'labels']
    inlines = [MachineRatingInline]

    # Utiliser des checkboxes pour les ManyToMany
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    def is_available_display(self, obj):
        if obj.is_available:
            return format_html('<span style="color: green;">✓ Disponible</span>')
        elif obj.is_maintenance:
            return format_html('<span style="color: orange;">🔧 Maintenance</span>')
        else:
            return format_html('<span style="color: red;">✗ Indisponible</span>')
    is_available_display.short_description = 'Statut'

    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'brand', 'model', 'machine_type', 'difficulty_level')
        }),
        ('Description et utilisation', {
            'fields': ('description', 'instructions', 'safety_notes')
        }),
        ('Groupes musculaires', {
            'fields': ('primary_muscles', 'secondary_muscles'),
            'classes': ('wide',)
        }),
        ('Catégorisation', {
            'fields': ('labels',),
            'classes': ('wide',)
        }),
        ('Caractéristiques techniques', {
            'fields': (
                ('supports_speed', 'supports_incline', 'supports_resistance'),
                ('min_weight', 'max_weight', 'weight_increment')
            )
        }),
        ('Emplacement et statut', {
            'fields': (
                'gym_location',
                ('is_active', 'is_maintenance'),
                'image'
            )
        }),
        ('Métadonnées', {
            'fields': ('popularity_score', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_active', 'mark_as_maintenance', 'mark_as_inactive']

    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True, is_maintenance=False)
        self.message_user(request, f'{updated} machine(s) marquée(s) comme active(s).')
    mark_as_active.short_description = "Marquer comme actif"

    def mark_as_maintenance(self, request, queryset):
        updated = queryset.update(is_maintenance=True)
        self.message_user(request, f'{updated} machine(s) mise(s) en maintenance.')
    mark_as_maintenance.short_description = "Mettre en maintenance"

    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False, is_maintenance=False)
        self.message_user(request, f'{updated} machine(s) désactivée(s).')
    mark_as_inactive.short_description = "Désactiver"


@admin.register(MachineRating)
class MachineRatingAdmin(admin.ModelAdmin):
    list_display = ['machine', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'machine__machine_type']
    search_fields = ['machine__name', 'user__email', 'comment']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Évaluation', {
            'fields': ('machine', 'user', 'rating', 'comment')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )