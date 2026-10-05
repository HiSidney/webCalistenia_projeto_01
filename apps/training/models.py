from django.conf import settings
from django.db import models


class Exercise(models.Model):

    METRIC_CHOICES = [
        ("repetitions", "Repetições"),
        ("weight", "Carga"),
        ("duration", "Duração"),
    ]

    name = models.CharField(
        max_length=100
    )

    description = models.TextField(
        blank=True
    )

    muscle_group = models.CharField(
        max_length=100,
        blank=True
    )

    metric = models.CharField(
        max_length=20,
        choices=METRIC_CHOICES,
        default="repetitions",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name



class TrainingPlan(models.Model):
    """
    Programa de treinamento de um usuário.

    Exemplo:
        Calistenia Iniciante
        Hipertrofia
        Preparação para Muscle Up
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="training_plans",
    )

    name = models.CharField(
        max_length=100,
    )

    description = models.TextField(
        blank=True,
    )

    active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.name


class PlannedWorkout(models.Model):
    """
    Um treino planejado dentro de um TrainingPlan.

    Exemplo:
        Segunda-feira - Push
        Quarta-feira - Pull
        Sexta-feira - Legs
    """

    WEEKDAY_CHOICES = [
        (0, "Segunda-feira"),
        (1, "Terça-feira"),
        (2, "Quarta-feira"),
        (3, "Quinta-feira"),
        (4, "Sexta-feira"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    training_plan = models.ForeignKey(
        TrainingPlan,
        on_delete=models.CASCADE,
        related_name="planned_workouts",
    )

    name = models.CharField(
        max_length=100,
    )

    weekday = models.PositiveSmallIntegerField(
        choices=WEEKDAY_CHOICES,
    )

    order = models.PositiveIntegerField(
        default=0,
    )

    notes = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["weekday", "order"]

    def __str__(self):
        return f"{self.training_plan.name} - {self.name}"


class PlannedExercise(models.Model):
    """
    Exercício planejado dentro de um treino.

    Exemplo:
        Flexão -> 4 séries de 10 repetições
        Dips   -> 3 séries de 8 repetições
    """

    planned_workout = models.ForeignKey(
        PlannedWorkout,
        on_delete=models.CASCADE,
        related_name="planned_exercises",
    )

    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name="planned_exercises",
    )

    order = models.PositiveIntegerField(
        default=0,
    )

    target_sets = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    target_repetitions = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    target_weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    target_duration = models.DurationField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.planned_workout.name} - {self.exercise.name}"


class Workout(models.Model):
    """
    Um treino que realmente foi realizado.
    """

    STATUS_CHOICES = [
        ("planned", "Planejado"),
        ("in_progress", "Em andamento"),
        ("completed", "Concluído"),
        ("cancelled", "Cancelado"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workouts",
    )

    planned_workout = models.ForeignKey(
        PlannedWorkout,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workouts",
    )

    name = models.CharField(
        max_length=100,
    )

    date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-date", "-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "planned_workout",
                    "date",
                ],
                condition=models.Q(
                    planned_workout__isnull=False
                ),
                name="unique_planned_workout_per_user_per_day",
            ),
        ]




class WorkoutExercise(models.Model):
    """
    Exercício que foi efetivamente realizado em um Workout.
    """

    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name="workout_exercises",
    )

    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name="workout_exercises",
    )

    planned_exercise = models.ForeignKey(
        PlannedExercise,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workout_exercises",
    )

    order = models.PositiveIntegerField(
        default=0,
    )

    notes = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.workout.name} - {self.exercise.name}"


class Set(models.Model):
    """
    Uma série efetivamente realizada.
    """

    workout_exercise = models.ForeignKey(
        WorkoutExercise,
        on_delete=models.CASCADE,
        related_name="sets",
    )

    number = models.PositiveIntegerField()

    repetitions = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    duration = models.DurationField(
        null=True,
        blank=True,
    )

    completed = models.BooleanField(
        default=False,
    )

    notes = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["number"]

        constraints = [
            models.UniqueConstraint(
                fields=["workout_exercise", "number"],
                name="unique_set_number_per_exercise",
            ),
        ]

    def __str__(self):
        return (
            f"{self.workout_exercise.exercise.name} "
            f"- Série {self.number}"
        )
