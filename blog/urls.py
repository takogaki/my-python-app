from django.urls import path
from . import views

app_name = "blog"
urlpatterns = [
    path('', views.frontpage, name="frontpage"),
    path("blog/create/", views.post_create, name="post_create"),
    path('blog/<slug:slug>/', views.post_detail, name="post_detail"),
]