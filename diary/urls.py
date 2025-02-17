from django.urls import path
from . import views


app_name = "diary"
urlpatterns = [
    path("", views.index, name="index"),
    # path('diary/index/', views.index, name='index'),
    path("page/create/", views.page_create, name="page_create"),
    path("pages/", views.page_list, name="page_list"),
    path("page/<uuid:pk>/", views.page_detail, name="page_detail"),
    path("page/<uuid:pk>/update/", views.page_update, name="page_update"),
    path("page/<uuid:pk>/delete/", views.page_delete, name="page_delete"),
    # path('my_diaries/', views.my_diary_list, name='my_diary_list'),
    path('user/<int:user_id>/diaries/', views.user_diary_list, name='user_diary_list'),
    path('diary/<int:diary_id>/edit/', views.page_update, name='page_update'),
    path("like/<int:pk>/", views.like_diary, name="like_diary"),  # いいね用のURL
    path('like/<uuid:pk>/', views.like_diary, name='like_diary'),  # いいねAPI
]


    
