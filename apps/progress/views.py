from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.training.models import Set


@login_required
def forca(request):

    sets = (
        Set.objects
        .filter(
            workout_exercise__workout__user=request.user,
            workout_exercise__workout__status="completed",
            completed=True,
        )
        .select_related(
            "workout_exercise__exercise",
            "workout_exercise__workout",
        )
        .order_by(
            "workout_exercise__exercise__name",
            "workout_exercise__workout__date",
            "workout_exercise__workout__id",
            "number",
        )
    )

    exercises = {}

    for workout_set in sets:

        exercise = workout_set.workout_exercise.exercise
        workout = workout_set.workout_exercise.workout

        exercise_id = exercise.id

        if exercise_id not in exercises:
            exercises[exercise_id] = {
                "exercise": exercise,
                "workouts": {},
            }

        workout_id = workout.id

        if workout_id not in exercises[exercise_id]["workouts"]:
            exercises[exercise_id]["workouts"][workout_id] = {
                "date": workout.date,
                "value": None,
            }

        data = exercises[exercise_id]["workouts"][workout_id]

        if exercise.metric == "repetitions":
            value = workout_set.repetitions

        elif exercise.metric == "weight":
            value = workout_set.weight

        elif exercise.metric == "duration":
            value = workout_set.duration

        else:
            value = None

        if value is not None:

            if data["value"] is None:
                data["value"] = value

            elif value > data["value"]:
                data["value"] = value

    for data in exercises.values():

        workouts = list(
            data["workouts"].values()
        )

        workouts.sort(
            key=lambda workout: workout["date"]
        )

        data["history"] = workouts

        values = [
            workout["value"]
            for workout in workouts
            if workout["value"] is not None
        ]

        data["best"] = (
            max(values)
            if values
            else None
        )

        data["last"] = (
            values[-1]
            if values
            else None
        )

        data["evolution"] = None

        if len(values) >= 2:
            data["evolution"] = (
                values[-1] - values[0]
            )

    return render(
        request,
        "progress/forca.html",
        {
            "exercises": exercises.values(),
        },
    )
