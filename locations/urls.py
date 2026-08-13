from django.urls import path

from . import views

app_name = "locations"

urlpatterns = [
    path(
        "update/",
        views.update_location,
        name="update_location",
    ),
    path(
        "nearby-recruits/",
        views.nearby_recruits,
        name="nearby_recruits"
    ),
]