from django.urls import include, path

from . import views


app_name = "progress"


urlpatterns = [
    path(
        "forca/",
        views.forca,
        name="forca",
    ),
]
