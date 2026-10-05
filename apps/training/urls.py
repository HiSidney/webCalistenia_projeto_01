from django.urls import path

from . import views


app_name = "training"

urlpatterns = [
    path("", views.training_home, name="home"),

    path(
        "programacao/",
        views.programacao,
        name="programacao",
    ),

    path(
        "historico/",
        views.historico,
        name="historico",
    ),

    path(
        "treino/iniciar/<int:planned_workout_id>/",
        views.iniciar_treino,
        name="iniciar_treino",
    ),

    path(
        "treino/<int:workout_id>/",
        views.treino_atual,
        name="treino_atual",
    ),
    path(
        "treino/<int:workout_id>/exercicio/<int:workout_exercise_id>/serie/",
        views.adicionar_serie,
        name="adicionar_serie",
    ),
    path(
        "treino/<int:workout_id>/finalizar/",
        views.finalizar_treino,
        name="finalizar_treino",
    ),
    path(
        "treino/<int:workout_id>/exercicio/<int:workout_exercise_id>/serie/<int:set_id>/concluir/",
        views.concluir_serie,
        name="concluir_serie",
    ),
    path(
        "treino/<int:workout_id>/exercicio/<int:workout_exercise_id>/serie/<int:set_id>/editar/",
        views.editar_serie,
        name="editar_serie",
    ),

    path(
        "treino/<int:workout_id>/exercicio/<int:workout_exercise_id>/serie/<int:set_id>/excluir/",
        views.excluir_serie,
        name="excluir_serie",
    ),


]
