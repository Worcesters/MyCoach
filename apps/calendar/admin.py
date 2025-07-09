from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import WorkoutPlan, CSVImport, CalendarEvent, WeeklyTemplate


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'scheduled_date', 'status_display',
        'duration_minutes', 'priority', 'is_active'
    ]
    list_filter = [
        'is_active', 'priority', 'repeat_type',
        'reminder_enabled', 'scheduled_date'
    ]
    search_fields = ['title', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'is_past_due', 'is_today']
    date_hierarchy = 'scheduled_date'

    def status_display(self, obj):
        if obj.workout_created:
            return format_html('<span style="color: green;">✓ Séance créée</span>')
        elif obj.is_past_due:
            return format_html('<span style="color: red;">⚠ En retard</span>')
        elif obj.is_today:
            return format_html('<span style="color: orange;">📅 Aujourd\'hui</span>')
        else:
            return format_html('<span style="color: blue;">📝 Planifiée</span>')
    status_display.short_description = 'Statut'

    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'template', 'title', 'description')
        }),
        ('Planification', {
            'fields': (
                'scheduled_date', 'duration_minutes', 'priority', 'is_active'
            )
        }),
        ('Répétition', {
            'fields': (
                'repeat_type', 'repeat_interval', 'repeat_until'
            )
        }),
        ('Notifications', {
            'fields': (
                'reminder_enabled', 'reminder_minutes_before'
            )
        }),
        ('Statut', {
            'fields': ('workout_created', 'is_past_due', 'is_today'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['create_workouts', 'activate_plans', 'deactivate_plans']

    def create_workouts(self, request, queryset):
        """Crée des séances d'entraînement pour les plans sélectionnés"""
        count = 0
        for plan in queryset:
            if not plan.workout_created:
                plan.create_workout()
                count += 1
        self.message_user(request, f'{count} séance(s) créée(s).')
    create_workouts.short_description = "Créer des séances d'entraînement"

    def activate_plans(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} plan(s) activé(s).')
    activate_plans.short_description = "Activer les plans"

    def deactivate_plans(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} plan(s) désactivé(s).')
    deactivate_plans.short_description = "Désactiver les plans"


@admin.register(CSVImport)
class CSVImportAdmin(admin.ModelAdmin):
    list_display = [
        'filename', 'user', 'status', 'progress_display',
        'success_rate', 'created_at', 'processed_at'
    ]
    list_filter = ['status', 'created_at', 'processed_at']
    search_fields = ['filename', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = [
        'created_at', 'processed_at', 'total_rows',
        'successful_imports', 'failed_imports', 'success_rate'
    ]

    def progress_display(self, obj):
        if obj.status == 'completed':
            color = '#28a745' if obj.success_rate >= 90 else '#ffc107'
            return format_html(
                '<span style="color: {};">{}/{} réussis</span>',
                color, obj.successful_imports, obj.total_rows
            )
        elif obj.status == 'failed':
            return format_html('<span style="color: red;">Échec</span>')
        elif obj.status == 'processing':
            return format_html('<span style="color: blue;">En cours...</span>')
        else:
            return format_html('<span style="color: gray;">En attente</span>')
    progress_display.short_description = 'Progression'

    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'file', 'filename', 'status')
        }),
        ('Résultats', {
            'fields': (
                'total_rows', 'successful_imports', 'failed_imports', 'success_rate'
            )
        }),
        ('Options et logs', {
            'fields': ('import_options', 'import_log', 'error_details')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'event_type', 'start_date',
        'duration_display', 'color_display'
    ]
    list_filter = ['event_type', 'all_day', 'start_date']
    search_fields = ['title', 'description', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'duration']
    date_hierarchy = 'start_date'

    def duration_display(self, obj):
        duration = obj.duration
        if duration:
            hours = duration.total_seconds() // 3600
            minutes = (duration.total_seconds() % 3600) // 60
            if hours > 0:
                return f"{int(hours)}h {int(minutes)}m"
            else:
                return f"{int(minutes)}m"
        return "Non défini"
    duration_display.short_description = 'Durée'

    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            obj.color, obj.color
        )
    color_display.short_description = 'Couleur'

    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'event_type', 'title', 'description', 'color')
        }),
        ('Temporalité', {
            'fields': (
                'start_date', 'end_date', 'all_day', 'duration'
            )
        }),
        ('Relations', {
            'fields': ('workout', 'workout_plan')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WeeklyTemplate)
class WeeklyTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'is_active', 'workout_days_count', 'created_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'workout_days_count']

    def workout_days_count(self, obj):
        """Compte le nombre de jours avec un template défini"""
        templates = [
            obj.monday_template, obj.tuesday_template, obj.wednesday_template,
            obj.thursday_template, obj.friday_template, obj.saturday_template,
            obj.sunday_template
        ]
        count = sum(1 for template in templates if template is not None)
        return f"{count}/7 jours"
    workout_days_count.short_description = 'Jours configurés'

    fieldsets = (
        ('Informations générales', {
            'fields': ('user', 'name', 'description', 'is_active')
        }),
        ('Templates par jour', {
            'fields': (
                'monday_template', 'tuesday_template', 'wednesday_template',
                'thursday_template', 'friday_template', 'saturday_template',
                'sunday_template'
            )
        }),
        ('Statistiques', {
            'fields': ('workout_days_count',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['activate_template', 'deactivate_template']

    def activate_template(self, request, queryset):
        """Active les templates sélectionnés"""
        for template in queryset:
            template.activate()
        self.message_user(request, 'Template(s) activé(s).')
    activate_template.short_description = "Activer le template"

    def deactivate_template(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} template(s) désactivé(s).')
    deactivate_template.short_description = "Désactiver le template"