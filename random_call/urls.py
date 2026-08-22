from django.urls import path

from . import views


app_name = "random_call"


urlpatterns = [
    path("", views.random_call, name="index"),

    path(
        "test/",
        views.random_call_test,
        name="test",
    ),
]