from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import (
    Workout, Exercise, Serie, WorkoutTemplate,
    PerformanceRecord, WorkoutProgram
)


class SerieInline(admin.TabularInline):
    model = Serie
    extra = 0
    readonly_fields = ['created_at', 'completed_at']
    fields = [
        'set_number', 'reps', 'weight', 'duration_seconds',
        'speed_kmh', 'incline_percentage', 'rpe',
        'completed', 'notes'
    ]


class ExerciseInline(admin.StackedInline):
    model = Exercise
    extra = 0
    readonly_fields = ['created_at']
    inlines = [SerieInline]

    fieldsets = (
        ('Configuration', {
            'fields': (
                'machine', 'order',
                ('target_sets', 'target_reps', 'target_weight'),
                ('target_duration_seconds', 'target_distance_meters'),
                'rest_seconds', 'auto_progression'
            )
        }),
        ('Statut', {
            'fields': ('completed', 'notes')
        }),
    )


@admin.register(WorkoutTemplate)
class WorkoutTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'created_by', 'difficulty_level',
        'target_duration_minutes', 'is_public', 'created_at'
    ]
    list_filter = ['is_public', 'difficulty_level', 'created_at']
    search_fields = ['name', 'description', 'tags']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'description', 'created_by', 'is_public')
        }),
        ('Configuration', {
            'fields': (
                'target_duration_minutes', 'difficulty_level', 'tags'
            )
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'date', 'status_display',
        'duration_display', 'total_exercises', 'total_sets'
    ]
    list_filter = ['status', 'date', 'difficulty_felt', 'satisfaction']
    search_fields = ['name', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = [
        'created_at', 'updated_at', 'total_exercises',
        'total_sets', 'total_volume'
    ]
    date_hierarchy = 'date'
    inlines = [ExerciseInline]

    def status_display(self, obj):
        colors = {
            'planned': '#ffc107',
            'in_progress': '#17a2b8',
            'completed': '#28a745',
            'cancelled': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Statut'

    def duration_display(self, obj):
        if obj.actual_duration_minutes:
            return f"{obj.actual_duration_minutes} min (réel)"
        return f"{obj.planned_duration_minutes} min (prévu)"
    duration_display.short_description = 'Durée'

    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'template', 'name', 'description', 'date')
        }),
        ('Durée et statut', {
            'fields': (
                'status',
                ('planned_duration_minutes', 'actual_duration_minutes'),
                ('started_at', 'completed_at')
            )
        }),
        ('Évaluation', {
            'fields': (
                ('difficulty_felt', 'satisfaction'),
                'notes'
            )
        }),
        ('Statistiques', {
            'fields': ('total_exercises', 'total_sets', 'total_volume'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_completed', 'mark_as_cancelled']

    def mark_as_completed(self, request, queryset):
        for workout in queryset:
            if workout.status in ['planned', 'in_progress']:
                workout.complete_workout()
        self.message_user(request, f'{queryset.count()} séance(s) marquée(s) comme terminée(s).')
    mark_as_completed.short_description = "Marquer comme terminé"

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} séance(s) annulée(s).')
    mark_as_cancelled.short_description = "Annuler les séances"


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = [
        'machine', 'workout', 'order', 'target_config',
        'progress_display', 'completed'
    ]
    list_filter = ['completed', 'auto_progression', 'machine__machine_type']
    search_fields = [
        'machine__name', 'workout__name',
        'workout__user__email'
    ]
    readonly_fields = ['created_at', 'completed_sets', 'progress_percentage']
    inlines = [SerieInline]

    def target_config(self, obj):
        if obj.target_weight:
            return f"{obj.target_sets}×{obj.target_reps} @ {obj.target_weight}kg"
        elif obj.target_duration_seconds:
            minutes = obj.target_duration_seconds // 60
            seconds = obj.target_duration_seconds % 60
            return f"{minutes}:{seconds:02d}"
        return f"{obj.target_sets}×{obj.target_reps}"
    target_config.short_description = 'Configuration'

    def progress_display(self, obj):
        percentage = obj.progress_percentage
        if percentage == 100:
            color = '#28a745'
        elif percentage >= 50:
            color = '#ffc107'
        else:
            color = '#dc3545'
        return format_html(
            '<div style="width: 50px; background: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; height: 15px; background: {}; border-radius: 3px;"></div>'
            '</div>',
            percentage, color
        )
    progress_display.short_description = 'Progression'


@admin.register(Serie)
class SerieAdmin(admin.ModelAdmin):
    list_display = [
        'exercise', 'set_number', 'performance_display',
        'rpe', 'completed', 'completed_at'
    ]
    list_filter = ['completed', 'rpe', 'created_at']
    search_fields = [
        'exercise__machine__name', 'exercise__workout__name',
        'exercise__workout__user__email'
    ]
    readonly_fields = ['created_at', 'completed_at', 'volume', 'estimated_1rm']

    def performance_display(self, obj):
        if obj.weight and obj.reps:
            return f"{obj.weight}kg × {obj.reps} reps"
        elif obj.duration_seconds:
            minutes = obj.duration_seconds // 60
            seconds = obj.duration_seconds % 60
            return f"{minutes}:{seconds:02d}"
        return "Non défini"
    performance_display.short_description = 'Performance'

    fieldsets = (
        ('Configuration', {
            'fields': ('exercise', 'set_number')
        }),
        ('Performance', {
            'fields': (
                ('reps', 'weight'),
                ('duration_seconds', 'distance_meters'),
                ('speed_kmh', 'incline_percentage')
            )
        }),
        ('Évaluation', {
            'fields': (
                ('rpe', 'rest_seconds_actual'),
                'notes', 'completed'
            )
        }),
        ('Calculs', {
            'fields': ('volume', 'estimated_1rm'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PerformanceRecord)
class PerformanceRecordAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'machine', 'record_type', 'record_display',
        'achieved_at', 'is_verified'
    ]
    list_filter = ['record_type', 'is_verified', 'achieved_at']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'machine__name'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'achieved_at'

    def record_display(self, obj):
        if obj.weight and obj.reps:
            return f"{obj.weight}kg × {obj.reps}"
        elif obj.duration_seconds:
            minutes = obj.duration_seconds // 60
            seconds = obj.duration_seconds % 60
            return f"{minutes}:{seconds:02d}"
        elif obj.distance_meters:
            return f"{obj.distance_meters}m"
        return "Record personnel"
    record_display.short_description = 'Record'

    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'machine', 'record_type', 'achieved_at')
        }),
        ('Valeurs du record', {
            'fields': (
                ('weight', 'reps'),
                ('duration_seconds', 'distance_meters')
            )
        }),
        ('Métadonnées', {
            'fields': (
                'workout', 'notes', 'is_verified', 'created_at'
            )
        }),
    )


@admin.register(WorkoutProgram)
class WorkoutProgramAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'created_by', 'duration_weeks',
        'workouts_per_week', 'difficulty_level', 'is_public'
    ]
    list_filter = ['is_public', 'difficulty_level', 'created_at']
    search_fields = ['name', 'description', 'tags']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['templates']

    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'description', 'created_by', 'is_public')
        }),
        ('Configuration', {
            'fields': (
                ('duration_weeks', 'workouts_per_week'),
                'difficulty_level', 'tags'
            )
        }),
        ('Templates', {
            'fields': ('templates',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )