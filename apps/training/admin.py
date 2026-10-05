from django.contrib import admin

from .models import (
    Exercise,
    TrainingPlan,
    PlannedWorkout,
    PlannedExercise,
    Workout,
    WorkoutExercise,
    Set,
)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "muscle_group",
        "created_at",
    )

    search_fields = (
        "name",
        "muscle_group",
    )


@admin.register(TrainingPlan)
class TrainingPlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "active",
        "created_at",
    )

    list_filter = (
        "active",
    )

    search_fields = (
        "name",
        "user__username",
    )


@admin.register(PlannedWorkout)
class PlannedWorkoutAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "training_plan",
        "weekday",
        "order",
    )

    list_filter = (
        "weekday",
    )

    search_fields = (
        "name",
        "training_plan__name",
    )


@admin.register(PlannedExercise)
class PlannedExerciseAdmin(admin.ModelAdmin):
    list_display = (
        "exercise",
        "planned_workout",
        "order",
        "target_sets",
        "target_repetitions",
        "target_weight",
    )

    search_fields = (
        "exercise__name",
        "planned_workout__name",
    )


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "date",
        "status",
        "started_at",
        "finished_at",
    )

    list_filter = (
        "status",
        "date",
    )

    search_fields = (
        "name",
        "user__username",
    )


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = (
        "workout",
        "exercise",
        "order",
    )

    search_fields = (
        "workout__name",
        "exercise__name",
    )


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = (
        "workout_exercise",
        "number",
        "repetitions",
        "weight",
        "duration",
        "completed",
    )

    list_filter = (
        "completed",
    )
