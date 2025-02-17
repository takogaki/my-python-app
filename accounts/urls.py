from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import SignUpView, UserDetailView
from . import views


app_name = "accounts"
urlpatterns = [
    path('signup/', SignUpView.as_view(template_name='accounts/signup.html'), name='signup'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('user_list/', views.user_list, name='user_list'),
    path('user_detail/<int:pk>/', views.user_detail, name='user_detail'),
    path("user/<str:username>/", UserDetailView.as_view(), name="user_detail"),
]