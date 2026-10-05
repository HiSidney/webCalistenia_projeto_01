from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone

from apps.training.models import (
    PlannedWorkout,
    Workout,
)

def get_next_workout(user, today_weekday):
    """
    Retorna o próximo treino programado depois de hoje.

    O treino de hoje nunca é retornado como
    'próximo treino'.
    """

    workouts = (
        PlannedWorkout.objects
        .filter(
            training_plan__user=user,
            training_plan__active=True,
        )
        .prefetch_related(
            "planned_exercises__exercise",
        )
        .order_by("weekday", "order")
    )

    # Primeiro procura um treino em um dia posterior
    next_workout = (
        workouts
        .filter(
            weekday__gt=today_weekday,
        )
        .first()
    )

    if next_workout:
        return next_workout

    # Se chegou ao final da semana,
    # procura a partir de segunda-feira,
    # mas exclui o dia de hoje.
    return (
        workouts
        .filter(
            weekday__lt=today_weekday,
        )
        .first()
    )



@login_required
def home(request):

    today = timezone.localdate()

    next_workout = get_next_workout(
        request.user,
        today.weekday(),
    )

    # --------------------------------------------------
    # TREINO EM ANDAMENTO
    # --------------------------------------------------

    current_workout = (
        Workout.objects
        .filter(
            user=request.user,
            status="in_progress",
        )
        .prefetch_related(
            "workout_exercises__exercise",
            "workout_exercises__sets",
        )
        .first()
    )

    # --------------------------------------------------
    # TREINO DE HOJE
    # --------------------------------------------------

    today_workout = (
        PlannedWorkout.objects
        .filter(
            training_plan__user=request.user,
            training_plan__active=True,
            weekday=today.weekday(),
        )
        .prefetch_related(
            "planned_exercises__exercise",
        )
        .first()
    )

    # --------------------------------------------------
    # ÚLTIMO TREINO CONCLUÍDO
    # --------------------------------------------------

    last_workout = (
        Workout.objects
        .filter(
            user=request.user,
            status="completed",
        )
        .prefetch_related(
            "workout_exercises__exercise",
            "workout_exercises__sets",
        )
        .order_by(
            "-date",
            "-finished_at",
        )
        .first()
    )

    # --------------------------------------------------
    # TOTAL DE TREINOS
    # --------------------------------------------------

    total_workouts = (
        Workout.objects
        .filter(
            user=request.user,
            status="completed",
        )
        .count()
    )

    # --------------------------------------------------
    # CONTAGEM DO ÚLTIMO TREINO
    # --------------------------------------------------

    last_workout_stats = {
        "sets": 0,
        "reps": 0,
        "duration_minutes": 0,
    }

    if last_workout:

        workout_exercises = last_workout.workout_exercises.all()

        last_workout_stats["sets"] = sum(
            exercise.sets.filter(completed=True).count()
            for exercise in workout_exercises
        )


        last_workout_stats["reps"] = sum(
            (
                workout_set.repetitions or 0
                for exercise in workout_exercises
                for workout_set in exercise.sets.all()
                if workout_set.completed
            )
        )

        if last_workout.started_at and last_workout.finished_at:

            duration = (
                last_workout.finished_at
                - last_workout.started_at
            )

            last_workout_stats["duration_minutes"] = (
                int(duration.total_seconds() // 60)
            )


    # --------------------------------------------------
    # CONTEXTO
    # --------------------------------------------------

    context = {
        "current_workout": current_workout,
        "today_workout": today_workout,
        "last_workout": last_workout,
        "total_workouts": total_workouts,
        "last_workout_stats": last_workout_stats,
        "next_workout": next_workout,
    }

    return render(
        request,
        "home/home.html",
        context,
    )
