from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import SetForm

from .models import (
    PlannedWorkout,
    Workout,
    WorkoutExercise,
    Set,
)


@login_required
def training_home(request):
    return render(
        request,
        "training/home.html",
    )


@login_required
def programacao(request):

    today = timezone.localdate()

    training_plans = (
        request.user.training_plans
        .filter(active=True)
        .prefetch_related(
            "planned_workouts__planned_exercises__exercise"
        )
    )

    for plan in training_plans:

        for planned_workout in plan.planned_workouts.all():

            planned_workout.today_workout = (
                Workout.objects
                .filter(
                    user=request.user,
                    planned_workout=planned_workout,
                    date=today,
                )
                .first()
            )

    return render(
        request,
        "training/programacao.html",
        {
            "training_plans": training_plans,
        },
    )



@login_required
def historico(request):

    workouts = (
        Workout.objects
        .filter(
            user=request.user,
            status="completed",
        )
        .prefetch_related(
            "workout_exercises__exercise",
            "workout_exercises__sets",
        )
        .order_by("-date", "-finished_at")
    )

    for workout in workouts:

        workout.exercise_count = (
            workout.workout_exercises.count()
        )

        workout.set_count = sum(
            exercise.sets.count()
            for exercise in workout.workout_exercises.all()
        )

        if workout.started_at and workout.finished_at:

            duration = (
                workout.finished_at
                - workout.started_at
            )

            workout.duration_minutes = (
                int(duration.total_seconds() // 60)
            )

        else:

            workout.duration_minutes = 0

    return render(
        request,
        "training/historico.html",
        {
            "workouts": workouts,
        },
    )


@login_required
def iniciar_treino(request, planned_workout_id):

    planned_workout = get_object_or_404(
        PlannedWorkout.objects.prefetch_related(
            "planned_exercises__exercise"
        ),
        id=planned_workout_id,
        training_plan__user=request.user,
        training_plan__active=True,
    )

    today = timezone.localdate()

    # -----------------------------------------
    # 1. JÁ EXISTE ESSE TREINO HOJE?
    # -----------------------------------------

    existing_workout = (
        Workout.objects
        .filter(
            user=request.user,
            planned_workout=planned_workout,
            date=today,
        )
        .first()
    )

    if existing_workout:

        return redirect(
            "training:treino_atual",
            workout_id=existing_workout.id,
        )

    # -----------------------------------------
    # 2. EXISTE OUTRO TREINO EM ANDAMENTO?
    # -----------------------------------------

    current_workout = (
        Workout.objects
        .filter(
            user=request.user,
            status="in_progress",
        )
        .first()
    )

    if current_workout:

        training_plans = (
            request.user.training_plans
            .filter(active=True)
            .prefetch_related(
                "planned_workouts__planned_exercises__exercise"
            )
        )

        return render(
            request,
            "training/programacao.html",
            {
                "training_plans": training_plans,
                "start_error": (
                    f"Você já possui o treino "
                    f"'{current_workout.name}' "
                    f"em andamento."
                ),
            },
        )

    # -----------------------------------------
    # 3. CRIAR NOVO WORKOUT
    # -----------------------------------------

    workout = Workout.objects.create(
        user=request.user,
        planned_workout=planned_workout,
        name=planned_workout.name,
        date=today,
        status="in_progress",
        started_at=timezone.now(),
    )

    # -----------------------------------------
    # 4. CRIAR OS EXERCÍCIOS
    # -----------------------------------------

    for planned_exercise in planned_workout.planned_exercises.all():

        WorkoutExercise.objects.create(
            workout=workout,
            exercise=planned_exercise.exercise,
            planned_exercise=planned_exercise,
            order=planned_exercise.order,
        )

    return redirect(
        "training:treino_atual",
        workout_id=workout.id,
    )






@login_required
def treino_atual(request, workout_id):
    workout = get_object_or_404(
        Workout.objects.prefetch_related(
            "workout_exercises__exercise",
            "workout_exercises__planned_exercise",
        ),
        id=workout_id,
        user=request.user,
    )

    return render(
        request,
        "training/treino_atual.html",
        {
            "workout": workout,
        },
    )

@login_required
def adicionar_serie(
    request,
    workout_id,
    workout_exercise_id,
):
    workout = get_object_or_404(
        Workout,
        id=workout_id,
        user=request.user,
    )

    if workout.status != "in_progress":
        return redirect(
            "training:treino_atual",
            workout_id=workout.id,
        )

    workout_exercise = get_object_or_404(
        WorkoutExercise,
        id=workout_exercise_id,
        workout=workout,
    )

    if request.method == "POST":

        form = SetForm(request.POST)

        if form.is_valid():

            workout_set = form.save(commit=False)

            workout_set.workout_exercise = workout_exercise

            last_set = (
                workout_exercise.sets
                .order_by("-number")
                .first()
            )

            workout_set.number = (
                last_set.number + 1
                if last_set
                else 1
            )

            workout_set.save()

            return redirect(
                "training:treino_atual",
                workout_id=workout.id,
            )

    else:
        form = SetForm()

    return render(
        request,
        "training/adicionar_serie.html",
        {
            "form": form,
            "workout": workout,
            "workout_exercise": workout_exercise,
        },
    )


@login_required
def concluir_serie(
    request,
    workout_id,
    workout_exercise_id,
    set_id,
):
    workout = get_object_or_404(
        Workout,
        id=workout_id,
        user=request.user,
    )

    if workout.status != "in_progress":
        return redirect(
            "training:treino_atual",
            workout_id=workout.id,
        )

    workout_exercise = get_object_or_404(
        WorkoutExercise,
        id=workout_exercise_id,
        workout=workout,
    )

    workout_set = get_object_or_404(
        Set,
        id=set_id,
        workout_exercise=workout_exercise,
    )

    if request.method == "POST":
        workout_set.completed = True
        workout_set.save(update_fields=["completed"])

    return redirect(
        "training:treino_atual",
        workout_id=workout.id,
    )



@login_required
def finalizar_treino(request, workout_id):
    workout = get_object_or_404(
        Workout,
        id=workout_id,
        user=request.user,
    )

    if request.method == "POST":
        if workout.status == "in_progress":
            workout.status = "completed"
            workout.finished_at = timezone.now()
            workout.save(
                update_fields=[
                    "status",
                    "finished_at",
                ]
            )

    return redirect(
        "training:historico"
    )



@login_required
def editar_serie(
    request,
    workout_id,
    workout_exercise_id,
    set_id,
):
    workout = get_object_or_404(
        Workout,
        id=workout_id,
        user=request.user,
    )

    if workout.status != "in_progress":
        return redirect(
            "training:treino_atual",
            workout_id=workout.id,
        )

    workout_exercise = get_object_or_404(
        WorkoutExercise,
        id=workout_exercise_id,
        workout=workout,
    )

    workout_set = get_object_or_404(
        Set,
        id=set_id,
        workout_exercise=workout_exercise,
    )

    if request.method == "POST":
        form = SetForm(
            request.POST,
            instance=workout_set,
        )

        if form.is_valid():
            form.save()

            return redirect(
                "training:treino_atual",
                workout_id=workout.id,
            )

    else:
        form = SetForm(instance=workout_set)

    return render(
        request,
        "training/editar_serie.html",
        {
            "form": form,
            "workout": workout,
            "workout_exercise": workout_exercise,
            "workout_set": workout_set,
        },
    )


@login_required
def excluir_serie(
    request,
    workout_id,
    workout_exercise_id,
    set_id,
):
    workout = get_object_or_404(
        Workout,
        id=workout_id,
        user=request.user,
    )

    if workout.status != "in_progress":
        return redirect(
            "training:treino_atual",
            workout_id=workout.id,
        )

    workout_exercise = get_object_or_404(
        WorkoutExercise,
        id=workout_exercise_id,
        workout=workout,
    )

    workout_set = get_object_or_404(
        Set,
        id=set_id,
        workout_exercise=workout_exercise,
    )

    if request.method == "POST":
        workout_set.delete()

    return redirect(
        "training:treino_atual",
        workout_id=workout.id,
    )

